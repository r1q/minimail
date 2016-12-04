from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.text import slugify
from celery import shared_task, group

from subscriber_management.models import List, Subscriber
from campaign_management.models import Campaign

import time
import base64
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup as HTMLParser
import traceback


def _inject_unsubscribe_link(subscriber, campaign, html_email_for_sending,
                             text_email_for_sending):
    # Build unsubscribe link
    unsubscribe_link = subscriber.unsubscribe_link()
    # Append current campaign uuid
    unsubscribe_link += "?c={}".format(campaign.uuid)
    # Inject the unsubscribe link into the HTML email
    html_email_for_sending = html_email_for_sending.replace('*%7CUNSUB%7C*',
                                                            unsubscribe_link)
    html_email_for_sending = html_email_for_sending.replace('*|UNSUB|*',
                                                            unsubscribe_link)
    # Inject the unsubscribe link into the text email
    text_email_for_sending = text_email_for_sending.replace('*%7CUNSUB%7C*',
                                                            unsubscribe_link)
    text_email_for_sending = text_email_for_sending.replace('*|UNSUB|*',
                                                            unsubscribe_link)
    return html_email_for_sending, text_email_for_sending, unsubscribe_link


def _inject_tracking_pixel(subscriber, email_list, campaign,
                           html_email_for_sending):
    """_inject_tracking_pixel

    Update campaign.html_email_for_sending inplace including the pixel
    to track open events.

    :param subscriber:
    :param email_list:
    :param campaign:
    """
    pixel_url = "http://minimail.fullweb.io/pixou/open/?list={}&campaign={}&subscriber={}"\
                .format(email_list.uuid, campaign.uuid, subscriber.uuid)
    tracking_snippet = '<img src="{}" height=1 width=1 /></body'.format(pixel_url)
    # Prepend closing </body> tag with <img> to tracking pixel
    html_email_for_sending = html_email_for_sending.replace('</body', tracking_snippet)
    return html_email_for_sending


def _convert_links_for_tracking(subscriber, email_list, campaign, html_email_for_sending):
    """_convert_links_for_tracking

    :param subscriber:
    :param email_list:
    :param campaign:
    """
    try:
        html_tree = HTMLParser(html_email_for_sending, "html5lib")
        all_links = html_tree.findAll('a')
        for link in all_links:
            if not link or not link.get('href') or not link.get('href', '').startswith('http'):
                continue
            try:
                #TODO: Fix corner case where URL is a click-to-share
                # UTM is added to the SNS share URL, not to the actual
                # shared link.
                ori_href = link.get('href').encode('utf8')
                parsed_ori_href = urlparse(ori_href)
                # Append UTM codes to original URL
                qs = parse_qs(parsed_ori_href.query)
                qs = {k.decode('utf8'): b"".join(v).decode('utf8') for k, v in qs.items()}
                qs['utm_medium'] = email_list.utm_medium or "email"
                qs['utm_source'] = email_list.utm_source or slugify(email_list.title)
                qs['utm_campaign'] = campaign.utm_campaign or slugify(campaign.email_subject)
                qs['utm_content'] = campaign.utm_content or ""
                qs['utm_term'] = campaign.utm_term or ""
                # Recontruct URL, first up to path
                url_to_track = "{}://{}{}?".format(parsed_ori_href.scheme.decode('utf8'),
                                                   parsed_ori_href.netloc.decode('utf8'),
                                                   parsed_ori_href.path.decode('utf8'))
                # Append querystring
                for k, v in qs.items():
                    if not v or v == "":
                        continue
                    if type(v) is list:
                        v = b",".join(v)
                    url_to_track += "{}={}&".format(k, v.strip())
                if url_to_track.endswith('&'):
                    url_to_track = url_to_track[:-1]
                # Append fragment
                url_to_track += parsed_ori_href.fragment.decode('utf8')
                # Wrap link with tracking
                b64_link = base64.b64encode(url_to_track.encode('utf8')).decode('utf8')
                link_tmpl = "http://minimail.fullweb.io/pixou/click/?list={}&campaign={}&subscriber={}&uri={}"
                new_link = link_tmpl.format(email_list.uuid, campaign.uuid,
                                            subscriber.uuid, b64_link)
                # Update HTML email
                link['href'] = new_link
            except Exception as ex:
                traceback.print_exc()
                print('error wrapping link', ex)
                continue
        html_email_for_sending = html_tree.prettify(formatter=None)
    except Exception as ex:
        print(ex)
    finally:
        return html_email_for_sending


def _gen_campaign_emails(campaign_id, list_id):
    """_gen_campaign_emails

    :param campaign_id:
    :param list_id:
    """
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        email_list = List.objects.get(id=list_id)
        subscribers = Subscriber.objects.filter(list__id=list_id, validated=True)
        # Get elements to personalize
        html_email_for_sending = campaign.html_email_for_sending
        text_email_for_sending = campaign.text_email
        # Build email headers common to all subscribers
        email_headers = {}
        email_headers['X-Mailer'] = "Minimail Mailer"
        email_headers['List-Id'] = "MINIMAIL-{}".format(email_list.uuid)
        email_headers['X-Campaign-Id'] = "MINIMAIL-{}".format(campaign.uuid)
        # Format sender field
        _from = "{} <{}>".format(campaign.email_from_name,
                                 campaign.email_list.from_email)
    except Exception as ex:
        print(ex)
        return tuple() # empty iterable

    for subscriber in subscribers:
        try:
            # TODO: Remember at what byte offset we inject the unsubscribe_link,
            #       to prevent O(n) search each time
            # ----
            # Add custom tracking open pixel for this subscriber
            html_email_for_sending = _inject_tracking_pixel(subscriber, email_list, campaign,
                                                            html_email_for_sending)
            # Convert all links to track clicks
            html_email_for_sending = _convert_links_for_tracking(subscriber, email_list, campaign,
                                                                 html_email_for_sending)
            # Add custom unsubscribe link for this subscriber
            html_email_for_sending, text_email_for_sending, unsubscribe_link = _inject_unsubscribe_link(subscriber,
                                                                                                        campaign,
                                                                                                        html_email_for_sending,
                                                                                                        text_email_for_sending)
            # Build current email headers
            curr_email_headers = {}
            curr_email_headers['List-Unsubscribe'] = "<{}>".format(unsubscribe_link)
            curr_email_headers['X-Recipient-ID'] = "{}".format(subscriber.uuid)
            curr_email_headers.update(email_headers)
            # Create email message object
            email = EmailMultiAlternatives(campaign.email_subject,  # email subject
                                           text_email_for_sending,  # body text version
                                           _from,  # from sender
                                           [subscriber.email],  # recipient
                                           reply_to=[campaign.email_reply_to_email],
                                           headers=curr_email_headers)
            email.attach_alternative(html_email_for_sending, "text/html")  # adding html email
        except Exception as ex:
            print(ex)
            email = False
        finally:
            yield email


@shared_task
def _send_one_newsletter_to_one_list(campaign_id, list_id):
    # Start the SMTP connection
    smtp_connection = get_connection()
    smtp_connection.open()
    # Send all emails
    for email in _gen_campaign_emails(campaign_id, list_id):
        try:
            if not email:
                print('email not sent', email)
                continue
            email.send()
        except Exception as ex:
            # TODO: Log fail to generate email
            print(email, ex)
            continue
    # Close connection
    smtp_connection.close()
