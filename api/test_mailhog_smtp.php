<?php
// MailHog ile SMTP Test (fsockopen ile direkt bağlantı)
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>📧 MailHog SMTP Test</h1>";
echo "<p><strong>MailHog Arayüzü:</strong> <a href='http://localhost:8025' target='_blank'>http://localhost:8025</a></p>";
echo "<hr>";

function sendMailToMailHog($to, $subject, $body) {
    $smtp = fsockopen('localhost', 1025, $errno, $errstr, 10);
    
    if (!$smtp) {
        return "❌ Bağlantı hatası: $errstr ($errno)";
    }
    
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>Sunucu: $response</pre>";
    
    // HELO
    fwrite($smtp, "HELO localhost\r\n");
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>HELO: $response</pre>";
    
    // MAIL FROM
    fwrite($smtp, "MAIL FROM:<katalog@localhost>\r\n");
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>MAIL FROM: $response</pre>";
    
    // RCPT TO
    fwrite($smtp, "RCPT TO:<{$to}>\r\n");
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>RCPT TO: $response</pre>";
    
    // DATA
    fwrite($smtp, "DATA\r\n");
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>DATA: $response</pre>";
    
    // Headers + Body
    $message = "From: katalog@localhost\r\n";
    $message .= "To: {$to}\r\n";
    $message .= "Subject: {$subject}\r\n";
    $message .= "MIME-Version: 1.0\r\n";
    $message .= "Content-type: text/html; charset=UTF-8\r\n";
    $message .= "\r\n";
    $message .= $body;
    $message .= "\r\n.\r\n";
    
    fwrite($smtp, $message);
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>Gönderim: $response</pre>";
    
    // QUIT
    fwrite($smtp, "QUIT\r\n");
    $response = fgets($smtp, 515);
    echo "<pre style='background:#f0f0f0;padding:10px'>QUIT: $response</pre>";
    
    fclose($smtp);
    
    return "✅ Mail başarıyla gönderildi!";
}

// Test mail içeriği
$to = 'info@muratboyraz.com';
$subject = 'Test Mail - ' . date('H:i:s');
$body = '<html><body style="font-family:Arial,sans-serif">';
$body .= '<h1 style="color:#2c3e50">🎉 Test Mail Başarılı!</h1>';
$body .= '<p>Bu mail MailHog üzerinden gönderildi.</p>';
$body .= '<p><strong>Tarih:</strong> ' . date('d.m.Y H:i:s') . '</p>';
$body .= '<hr>';
$body .= '<h2>Sipariş Detayları (Test)</h2>';
$body .= '<table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse">';
$body .= '<tr style="background:#3498db;color:white"><th>Ürün</th><th>Adet</th><th>Fiyat</th></tr>';
$body .= '<tr><td>Test Ürün 1</td><td>2</td><td>100 TL</td></tr>';
$body .= '<tr><td>Test Ürün 2</td><td>1</td><td>50 TL</td></tr>';
$body .= '<tr style="background:#ecf0f1"><th colspan="2">TOPLAM</th><th>250 TL</th></tr>';
$body .= '</table>';
$body .= '<hr>';
$body .= '<p style="color:#7f8c8d;font-size:12px">Bu bir test mailidir.</p>';
$body .= '</body></html>';

echo "<h3>📤 Mail Gönderiliyor...</h3>";
echo "<p><strong>Alıcı:</strong> {$to}</p>";
echo "<p><strong>Konu:</strong> {$subject}</p>";
echo "<hr>";

$result = sendMailToMailHog($to, $subject, $body);

echo "<hr>";
echo "<h2 style='color:green'>{$result}</h2>";
echo "<hr>";
echo "<h3>🔍 Maili görüntülemek için:</h3>";
echo "<ol>";
echo "<li><strong><a href='http://localhost:8025' target='_blank'>MailHog Arayüzünü</a> açın ve yenileyin</strong></li>";
echo "<li>Gönderilen mail listede görünecek</li>";
echo "<li>Mailin HTML içeriğini görüntüleyebilirsiniz</li>";
echo "</ol>";
?>
