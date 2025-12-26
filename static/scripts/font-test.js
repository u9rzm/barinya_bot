// Тест загрузки шрифтов
function testFonts() {
  const fonts = [
    'Enthalpy298',
    'FuturaNewCondBook', 
    'TTHoves'
  ];

  fonts.forEach(font => {
    if (document.fonts.check(`16px "${font}"`)) {
      console.log(`✅ Шрифт ${font} загружен`);
    } else {
      console.warn(`⚠️ Шрифт ${font} не загружен`);
    }
  });
}

// Проверяем после загрузки всех шрифтов
document.fonts.ready.then(() => {
  console.log('🎨 Все шрифты загружены');
  testFonts();
});

// Экспортируем для использования в консоли
window.testFonts = testFonts;