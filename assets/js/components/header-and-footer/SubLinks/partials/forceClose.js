export default function forceClose(nodes) {

  const closeAllMenus = () => {
    window.componentInterfaces.NavBar.forEach((instance) => {
      instance.methods.closeMobile();
    });
  };

  if (nodes.length > 0) {
    for (let i = 0; nodes.length > i; i++) {
      const link = nodes[i];

      if (link.classList.contains('js-link')) {
        link.addEventListener('click', closeAllMenus);
      }
    }
  }
}
