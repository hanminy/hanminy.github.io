(() => {
  const input = document.querySelector('#search');
  const cards = [...document.querySelectorAll('.site-card')];
  const filters = [...document.querySelectorAll('.filter')];
  let category = 'all';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko').trim();
  function update() {
    const query = normalize(input.value);
    let count = 0;
    cards.forEach(card => {
      card.hidden = !(category === 'all' || card.dataset.category === category) || !normalize(card.dataset.search).includes(query);
      if (!card.hidden) count++;
    });
    document.querySelector('#result-count').textContent = `${count}개의 사이트`;
    document.querySelector('#empty').hidden = count > 0;
    filters.forEach(button => {
      const active = button.dataset.category === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  input.addEventListener('input', update);
  filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.category; update(); }));
  document.querySelector('#reset').addEventListener('click', () => { category = 'all'; input.value = ''; update(); input.focus(); });
})();
