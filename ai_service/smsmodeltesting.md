C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -d "{\"content\": \"URGENT: Your account has been compromised! Verify immediately at http://fakebank-secure-login.com to avoid suspension.\", \"channel\": \"sms\", \"sender_info\": \"555-9876\"}"
{"analysis_id":"sms_20250913_075403_713597","channel":"sms","risk_score":0.423835186958313,"risk_level":"HIGH","is_fraud":true,"triggers":[],"explanation":"AI detected spam with 98.5% confidence","confidence":0.9845879673957825,"processing_time":0.07460379600524902,"timestamp":"2025-09-13T07:54:03.788201","highlighted_tokens":[{"text":"URGENT","start":0,"end":6,"category":"urgency","risk_level":"medium"},{"text":"immediately","start":50,"end":61,"category":"urgency","risk_level":"medium"},{"text":"Verify","start":43,"end":49,"category":"otp_verification","risk_level":"medium"}],"detailed_analysis":null}
C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -d "{\"content\": \"BANK ALERT: Unusual activity detected. Verify account at https://secure-bank.com or account will be closed.\", \"channel\": \"sms\", \"sender_info\": \"555-0456\"}"
{"analysis_id":"sms_20250913_075439_693693","channel":"sms","risk_score":0.29284348964691165,"risk_level":"MEDIUM","is_fraud":true,"triggers":[],"explanation":"No significant scam indicators detected","confidence":0.657108724117279,"processing_time":0.0794839859008789,"timestamp":"2025-09-13T07:54:39.773177","highlighted_tokens":[{"text":"BANK","start":0,"end":4,"category":"authority","risk_level":"medium"},{"text":"closed","start":82,"end":88,"category":"authority","risk_level":"medium"},{"text":"Verify","start":39,"end":45,"category":"otp_verification","risk_level":"medium"}],"detailed_analysis":null}
C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -d "{\"content\": \"CONGRATULATIONS! You have won $5000! Call 555-0456 to claim your prize.\", \"channel\": \"sms\", \"sender_info\": \"555-0456\"}"
{"analysis_id":"sms_20250913_075510_279364","channel":"sms","risk_score":0.39966716766357424,"risk_level":"MEDIUM","is_fraud":true,"triggers":[],"explanation":"AI detected spam with 99.9% confidence","confidence":0.9991679191589355,"processing_time":0.07356524467468262,"timestamp":"2025-09-13T07:55:10.352929","highlighted_tokens":[],"detailed_analysis":null}
C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -d "{\"content\": \"Your account balance is $1500. Thank you for banking with us.\", \"channel\": \"sms\", \"sender_info\": \"555-0789\"}"
{"analysis_id":"sms_20250913_075550_256158","channel":"sms","risk_score":0.0,"risk_level":"LOW","is_fraud":false,"triggers":[],"explanation":"No significant scam indicators detected","confidence":0.9956110119819641,"processing_time":0.06580710411071777,"timestamp":"2025-09-13T07:55:50.321965","highlighted_tokens":[],"detailed_analysis":null}
C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" \
{"detail":[{"type":"missing","loc":["body"],"msg":"Field required","input":null,"url":"https://errors.pydantic.dev/2.5/v/missing"}]}curl: (3) URL rejected: Bad hostname

C:\Users\GARV>  -H "Content-Type: application/json" \
'-H' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\GARV>  -d "{\"content\": \"⚠️ ALERT: Your PayPal account is temporarily locked due to suspicious activity. Confirm your identity within 24 hours at https://paypal-secure-help.com to restore access.\", \"channel\": \"sms\", \"sender_info\": \"555-0912\"}"
'-d' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\GARV>C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" ^
More?   -H "Content-Type: application/json" ^
More?   -d "{\"content\": \"⚠️ ALERT: Your PayPal account is temporarily locked due to suspicious activity. Confirm your identity within 24 hours at https://paypal-secure-help.com to restore access.\", \"channel\": \"sms\", \"sender_info\": \"555-0912\"}"
'C:\Users\GARV' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\GARV>curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -d "{\"content\": \"⚠️ ALERT: Your PayPal account is temporarily locked due to suspicious activity. Confirm your identity within 24 hours at https://paypal-secure-help.com to restore access.\", \"channel\": \"sms\", \"sender_info\": \"555-0912\"}"
{"analysis_id":"sms_20250913_075730_436719","channel":"sms","risk_score":0.4174749326705933,"risk_level":"HIGH","is_fraud":true,"triggers":[],"explanation":"AI detected spam with 99.4% confidence","confidence":0.9936873316764832,"processing_time":0.10251927375793457,"timestamp":"2025-09-13T07:57:30.539238","highlighted_tokens":[{"text":"PayPal","start":15,"end":21,"category":"payment","risk_level":"medium"},{"text":"Confirm","start":80,"end":87,"category":"otp_verification","risk_level":"medium"}],"detailed_analysis":null}
C:\Users\GARV>