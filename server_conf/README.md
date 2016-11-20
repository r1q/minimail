## Nginx

Version: `1.11.6`

Log files:

* `minimail.axx.log`: Every app request (excluding static files)
* `minimail.err.log`: Any errors

* `minimail.pixou.open.axx.log`: Open email
* `minimail.pixou.click.axx.log`: Click email link

* `minimail.pixou.ses.any.axx.log`: SES any callback
* `minimail.pixou.ses.delivery.axx.log`: SES email delivery
* `minimail.pixou.ses.bounce.axx.log`: SES email bounce
* `minimail.pixou.ses.complaint.axx.log`: SES email complaint

Compiling:

```bash
./configure
    --with-file-aio \
    --with-threads \
    --with-http_realip_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-stream \
    --with-stream_ssl_module
 ```
