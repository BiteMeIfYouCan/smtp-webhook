一个简单的邮件发送系统,通过web发送邮件，支持多账号，抄送等，适用于某些环境

调用示例：
```
curl -X POST http://mail:8080/send \
  -H "Content-Type: application/json" \
  -d '{
        "token":   "1234567890abcdef",
        "smtp_id": "default",
        "to":      "mail@xx.com",
        "cc":      "cc@mail.com",      # 可省略
        "subject": "测试邮件",
        "body":    "这是邮件主体!"
      }'
```
