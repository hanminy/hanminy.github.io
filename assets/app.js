(() => {
  const input = document.querySelector('#search');
  const cards = [...document.querySelectorAll('.site-card')];
  const groups = [...document.querySelectorAll('.group')];
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko').trim();
  function update() {
    const query = normalize(input.value);
    let count = 0;
    cards.forEach(card => {
      card.hidden = !normalize(card.dataset.search).includes(query);
      if (!card.hidden) count++;
    });
    groups.forEach(group => { group.hidden = !group.querySelector('.site-card:not([hidden])'); });
    document.querySelector('#result-count').textContent = `${count}개의 사이트`;
    document.querySelector('#empty').hidden = count > 0;
  }
  input.addEventListener('input', update);
  document.querySelector('#reset').addEventListener('click', () => { input.value = ''; update(); input.focus(); });
})();
