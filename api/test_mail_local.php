<?php
// Lokal mail testi
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Test data
$testData = [
    'sender_name' => 'Test Kullanıcı',
    'sender_company' => 'Test Firma',
    'sender_phone' => '0555 123 4567',
    'sender_email' => 'info@muratboyraz.com',
    'order_code' => 'TEST-' . date('Ymd-His'),
    'items' => [
        [
            'sku' => 'TEST-001',
            'brand' => 'Test Marka',
            'name' => 'Test Ürün',
            'qty' => 2,
            'price_value' => 100.50
        ]
    ]
];

$senderName = $testData['sender_name'];
$senderCompany = $testData['sender_company'];
$senderPhone = $testData['sender_phone'];
$senderEmail = $testData['sender_email'];
$code = $testData['order_code'];
$items = $testData['items'];

// HTML oluştur
$rows = "";
$total = 0;
foreach ($items as $it) {
    $sku = htmlspecialchars($it['sku'], ENT_QUOTES, 'UTF-8');
    $name = htmlspecialchars($it['name'], ENT_QUOTES, 'UTF-8');
    $brand = htmlspecialchars($it['brand'], ENT_QUOTES, 'UTF-8');
    $qty = intval($it['qty']);
    $price = floatval($it['price_value']);
    $line = $qty * $price;
    $total += $line;
    
    $rows .= "<tr><td style='padding:8px;border:1px solid #ddd'>{$sku}</td><td style='padding:8px;border:1px solid #ddd'>{$brand}</td><td style='padding:8px;border:1px solid #ddd'>{$name}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>{$qty}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($price, 2, ',', '.') . " TL</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($line, 2, ',', '.') . " TL</td></tr>";
}

$body = "<div style='font-family:Arial,sans-serif;max-width:800px'><h2>🛒 Yeni Sepet Talebi</h2><p><strong>Talep Kodu:</strong> {$code}</p><hr><h3>Müşteri Bilgileri</h3><p><strong>Ad Soyad:</strong> {$senderName}</p><p><strong>Firma:</strong> {$senderCompany}</p><p><strong>Telefon:</strong> {$senderPhone}</p><p><strong>E-posta:</strong> {$senderEmail}</p><h3>Sipariş Detayları</h3><table style='width:100%;border-collapse:collapse'><thead><tr style='background:#f5f5f5'><th style='padding:8px;border:1px solid #ddd;text-align:left'>SKU</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Marka</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Ürün</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Adet</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Birim Fiyat</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Toplam</th></tr></thead><tbody>{$rows}</tbody><tfoot><tr><td colspan='5' style='padding:8px;border:1px solid #ddd;text-align:right'><strong>Genel Toplam</strong></td><td style='padding:8px;border:1px solid #ddd;text-align:right'><strong>" . number_format($total, 2, ',', '.') . " TL</strong></td></tr></tfoot></table><p style='margin-top:20px;color:#999;font-size:12px'>Gönderim: " . date('d.m.Y H:i:s') . "</p></div>";

$subject = "B2B Sepet Talebi: {$code}";
$headers = "MIME-Version: 1.0\r\n";
$headers .= "Content-type: text/html; charset=UTF-8\r\n";
$headers .= "From: katalog@vivarel.com.tr\r\n";
$headers .= "Reply-To: {$senderEmail}\r\n";
$headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";

echo "<h1>Mail Test</h1>";
echo "<h2>Test Bilgileri:</h2>";
echo "<p><strong>Gönderen:</strong> {$senderEmail}</p>";
echo "<p><strong>Alıcı:</strong> info@muratboyraz.com</p>";
echo "<p><strong>Konu:</strong> {$subject}</p>";

// Mail göndermeyi dene
echo "<h2>Mail Gönderiliyor...</h2>";
$sent = mail("info@muratboyraz.com", $subject, $body, $headers);

if ($sent) {
    echo "<p style='color:green;font-size:18px'>✅ Mail başarıyla gönderildi!</p>";
    echo "<p>Mail kutunuzu kontrol edin (spam klasörüne de bakın)</p>";
} else {
    echo "<p style='color:red;font-size:18px'>❌ Mail gönderilemedi!</p>";
    $lastError = error_get_last();
    echo "<p><strong>Hata:</strong> " . ($lastError['message'] ?? 'Bilinmiyor') . "</p>";
    echo "<p><strong>Mail fonksiyonu mevcut mu:</strong> " . (function_exists('mail') ? 'Evet' : 'Hayır') . "</p>";
}

echo "<hr>";
echo "<h2>Mail İçeriği (Önizleme):</h2>";
echo $body;

echo "<hr>";
echo "<h2>Mail Headers:</h2>";
echo "<pre>" . htmlspecialchars($headers) . "</pre>";

echo "<hr>";
echo "<h2>PHP Bilgileri:</h2>";
echo "<pre>";
echo "PHP Version: " . phpversion() . "\n";
echo "OS: " . PHP_OS . "\n";
echo "SAPI: " . php_sapi_name() . "\n";
echo "sendmail_path: " . ini_get('sendmail_path') . "\n";
echo "SMTP: " . ini_get('SMTP') . "\n";
echo "smtp_port: " . ini_get('smtp_port') . "\n";
echo "</pre>";
