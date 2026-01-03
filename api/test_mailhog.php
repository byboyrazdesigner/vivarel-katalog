<?php
// MailHog ile Lokal Test
error_reporting(E_ALL);
ini_set('display_errors', 1);

// MailHog SMTP ayarları
ini_set('SMTP', 'localhost');
ini_set('smtp_port', '1025');
ini_set('sendmail_from', 'test@localhost');

echo "<h1>📧 MailHog Test</h1>";
echo "<p><strong>MailHog Web Arayüzü:</strong> <a href='http://localhost:8025' target='_blank'>http://localhost:8025</a></p>";
echo "<hr>";

// Test mail gönder
$to = 'info@muratboyraz.com';
$subject = 'Test Mail - ' . date('H:i:s');
$message = '<html><body>';
$message .= '<h1>Test Mail Başarılı! 🎉</h1>';
$message .= '<p>Bu mail MailHog üzerinden gönderildi.</p>';
$message .= '<p>Zaman: ' . date('d.m.Y H:i:s') . '</p>';
$message .= '<hr>';
$message .= '<h2>Sipariş Detayları (Test)</h2>';
$message .= '<table border="1" cellpadding="10">';
$message .= '<tr><th>Ürün</th><th>Adet</th><th>Fiyat</th></tr>';
$message .= '<tr><td>Test Ürün 1</td><td>2</td><td>100 TL</td></tr>';
$message .= '<tr><td>Test Ürün 2</td><td>1</td><td>50 TL</td></tr>';
$message .= '<tr><th colspan="2">TOPLAM</th><th>250 TL</th></tr>';
$message .= '</table>';
$message .= '</body></html>';

$headers = "MIME-Version: 1.0\r\n";
$headers .= "Content-type: text/html; charset=UTF-8\r\n";
$headers .= "From: katalog@localhost\r\n";
$headers .= "Reply-To: test@localhost\r\n";

echo "<p>📤 Mail gönderiliyor...</p>";

$result = mail($to, $subject, $message, $headers);

if ($result) {
    echo "<h2 style='color:green'>✅ Mail başarıyla gönderildi!</h2>";
    echo "<p><strong>Mail:</strong> {$to}</p>";
    echo "<p><strong>Konu:</strong> {$subject}</p>";
    echo "<hr>";
    echo "<h3>🔍 Maili görüntülemek için:</h3>";
    echo "<ol>";
    echo "<li><a href='http://localhost:8025' target='_blank'>http://localhost:8025</a> adresini açın</li>";
    echo "<li>Gönderilen maili listede göreceksiniz</li>";
    echo "<li>Mailin HTML içeriğini görüntüleyebilirsiniz</li>";
    echo "</ol>";
} else {
    echo "<h2 style='color:red'>❌ Mail gönderilemedi!</h2>";
    $error = error_get_last();
    echo "<pre>" . print_r($error, true) . "</pre>";
}

echo "<hr>";
echo "<p><strong>ℹ️ Not:</strong> Bu sadece lokal test için. Gerçek mail göndermez.</p>";
?>
