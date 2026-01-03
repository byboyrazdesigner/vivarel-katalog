<?php
// Gmail SMTP ile test maili
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Gmail ayarları (SIZIN gmail hesabınızı kullanın)
$gmailUser = 'sizin-gmail@gmail.com';  // BURAYA KENDI GMAIL ADRESINIZI YAZIN
$gmailPass = 'uygulama-sifresi';        // Gmail App Password (https://myaccount.google.com/apppasswords)

// Test data
$to = 'info@muratboyraz.com';
$subject = 'Test Mail - ' . date('H:i:s');
$body = '<h1>Test Mail</h1><p>Bu bir test mailidir.</p><p>Gönderim: ' . date('d.m.Y H:i:s') . '</p>';

echo "<h1>🧪 Gmail SMTP Test</h1>";
echo "<p><strong>Alıcı:</strong> {$to}</p>";
echo "<p><strong>Konu:</strong> {$subject}</p>";
echo "<hr>";

// SMTP ile mail gönder (fsockopen)
function sendGmailSMTP($to, $subject, $body, $gmailUser, $gmailPass) {
    $smtp = fsockopen('ssl://smtp.gmail.com', 465, $errno, $errstr, 30);
    
    if (!$smtp) {
        return "Bağlantı hatası: $errstr ($errno)";
    }
    
    $response = fgets($smtp, 515);
    echo "<pre>S: $response</pre>";
    
    // EHLO
    fwrite($smtp, "EHLO localhost\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: EHLO localhost\nS: $response</pre>";
    
    // AUTH LOGIN
    fwrite($smtp, "AUTH LOGIN\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: AUTH LOGIN\nS: $response</pre>";
    
    fwrite($smtp, base64_encode($gmailUser) . "\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: [username]\nS: $response</pre>";
    
    fwrite($smtp, base64_encode($gmailPass) . "\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: [password]\nS: $response</pre>";
    
    if (strpos($response, '235') === false) {
        fclose($smtp);
        return "❌ Giriş başarısız! Gmail App Password oluşturun: https://myaccount.google.com/apppasswords";
    }
    
    // MAIL FROM
    fwrite($smtp, "MAIL FROM:<{$gmailUser}>\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: MAIL FROM\nS: $response</pre>";
    
    // RCPT TO
    fwrite($smtp, "RCPT TO:<{$to}>\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: RCPT TO\nS: $response</pre>";
    
    // DATA
    fwrite($smtp, "DATA\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: DATA\nS: $response</pre>";
    
    // Headers + Body
    $message = "From: {$gmailUser}\r\n";
    $message .= "To: {$to}\r\n";
    $message .= "Subject: {$subject}\r\n";
    $message .= "MIME-Version: 1.0\r\n";
    $message .= "Content-type: text/html; charset=UTF-8\r\n";
    $message .= "\r\n";
    $message .= $body;
    $message .= "\r\n.\r\n";
    
    fwrite($smtp, $message);
    $response = fgets($smtp, 515);
    echo "<pre>C: [message]\nS: $response</pre>";
    
    // QUIT
    fwrite($smtp, "QUIT\r\n");
    $response = fgets($smtp, 515);
    echo "<pre>C: QUIT\nS: $response</pre>";
    
    fclose($smtp);
    
    return "✅ Mail gönderildi!";
}

$result = sendGmailSMTP($to, $subject, $body, $gmailUser, $gmailPass);

echo "<hr>";
echo "<h2>{$result}</h2>";

if (strpos($result, '✅') !== false) {
    echo "<p style='color:green'>Mail başarıyla gönderildi! <strong>{$to}</strong> adresini kontrol edin.</p>";
} else {
    echo "<p style='color:red'>{$result}</p>";
}
