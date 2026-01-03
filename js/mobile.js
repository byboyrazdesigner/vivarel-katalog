(function(){
  const panel   = document.querySelector('.chat-panel');
  const overlay = document.getElementById('chatOverlay');
  const fab     = document.getElementById('fabChat');
  if (!panel || !overlay || !fab) return;

  let openState = false;
  let closing   = false;

  const open = () => {
    if (openState || closing) return;
    openState = true;
    panel.classList.add('is-mobile-open');
    overlay.classList.add('open');
    document.body.classList.add('ai-sheet-open');
  };

  const close = () => {
    if (!openState || closing) return;
    closing = true;
    panel.classList.remove('is-mobile-open');
    overlay.classList.remove('open');
    document.body.classList.remove('ai-sheet-open');
    // iOS repaint güvenliği
    setTimeout(()=>{ closing = false; openState = false; }, 180);
  };

  const toggle = () => (openState ? close() : open());

  fab.addEventListener('click', toggle, { passive:true });
  overlay.addEventListener('click', close, { passive:true });
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') close(); });

  // Dışarıdan kontrol için:
  window.Mobile = { openChat: open, closeChat: close, toggleChat: toggle };
})();
