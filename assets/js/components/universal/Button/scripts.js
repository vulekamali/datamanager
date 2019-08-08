function scripts() {
  const nodesList = document.getElementsByClassName('Button js-pageLoad ');

  for (let i = 0; i < nodesList.length; i++) {
    if (window.CSS && window.CSS.supports('animation-name', 'spin')) {
      const node = nodesList[i];
      const addLoader = (event) => {
        event.target.innerHTML = '&nbsp;<div class="Button-loader"></div>';
      };
      node.addEventListener('click', addLoader);
    }
  }
}


export default scripts();

