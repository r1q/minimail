from django.core.mail import get_connection, EmailMultiAlternatives
from celery import shared_task, group

from subscriber_management.models import List, Subscriber
from campaign_management.models import Campaign

import time


def _inject_unsubscribe_link(subscriber, campaign):
    unsubscribe_link = subscriber.unsubscribe_link()
    html_email = campaign.html_email_for_sending.replace('*%7CUNSUB%7C*',
                                             unsubscribe_link)
    text_email = campaign.text_email.replace('*%7CUNSUB%7C*',
                                             unsubscribe_link)
    html_email = campaign.html_email_for_sending.replace('*|UNSUB|*',
                                             unsubscribe_link)
    text_email = campaign.text_email.replace('*|UNSUB|*',
                                             unsubscribe_link)
    return html_email, text_email


def _gen_campaign_emails(campaign_id, list_id):
    """_make_newsletter_emails

    :param campaign:
    """
    # If we got a campaign
    campaign = Campaign.objects.get(pk=campaign_id)
    subscribers = Subscriber.objects.filter(list__id=list_id,
                                            validated=True)
    for subscriber in subscribers:
        try:
            # TODO: Remember at what byte offset we inject the  unsubscribe_link,
            #       to prefer string O(n) search each time
            html_email, text_email = _inject_unsubscribe_link(subscriber, campaign)
            # TODO: Inject tracking pixel
            _from = "{} <{}>".format(campaign.email_from_name,
                                     campaign.email_list.from_email)
            email = EmailMultiAlternatives(campaign.email_subject,  # email subject
                                           text_email,  # body text version
                                           _from,  # from sender
                                           [subscriber.email],  # recipient
                                           reply_to=[campaign.email_reply_to_email])
            email.attach_alternative(html_email, "text/html")
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
    # TODO: Should be done concurrently
    for email in _gen_campaign_emails(campaign_id, list_id):
        try:
            email.send()
        except Exception as ex:
            # TODO: Log fail to generate email
            print(email.to, ex)
            continue
    # Close connection
    smtp_connection.close()
