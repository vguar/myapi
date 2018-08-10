# Dynamic rules configuration file
# Format :
#  <FILTER 1> [, <FILTER 2>, <FILTER ...>], <ACTION 1> [, <ACTION 2>, <ACTION ...>]
#
# FILTER :  <field><op><value>
#    field : API (api name), USER (token/user), USERFAMILY (token/user family), IP (remote ip address),
#            ENV (execution environment)
#            URL (http://host/...?param=val), METHOD (GET, POST...),
#            REQHEAD (request headers), REQBODY (request body)
#            RSPHEAD (response headers), RSPBODY (response body), RSPCODE (response code)
#            RSP==1 (force evaluation after generation of response)
#            @field  (request json field path)
#            @@field (response json field path)
#       op : == (equal), != (not equal)
#            =~ (regexp matching), !~ (regexp not matching), =~~ (icase regexp matching), !~~ (icase regexp not matching)
#      val : ...
#
# ACTION : <name>=<value>[:<option1>=<value>:<option2>=<value2>...]
#    name : DEBUG      : (0, 1, 2)
#           LOGBODY    : (0:no log, 1:request (default), 2:response, 3:request+response)
#           AUDIT      : (0:no audit, 1:request, 2:response, 3:request+response)
#           NOCACHE    : (1 to disable cache)
#           SLEEP      : (seconds)
#           ERROR      : (http code) [ + options: status, message ]
#           ADDHEAD    : (http header) [ + option value ]
#           ADDREQFIELD: (json field) [ + option value ]
#           ADDRSPFIELD: (json field) [ + option value ]
#           LOG        : (text) [ + option facility ]
#
# examples :
#   API==HostsList, IP=~127.*, DEBUG=2, ERROR=500:status=3:message=generic error, SLEEP=1
#   RSPBODY=~test, IP==127.0.0.1, ADDHEAD=X-Test:value=12345
#   RSPCODE==200, LOG=test:level=ERROR
#   @/ip==1.2.3.4, ADDREQFIELD=/ip:value=2.3.4.5
#   @@/_metadata/status==0, LOG=good
#   RSP==1, ADDRSPFIELD=/_metadata/newvar:value=test
#
