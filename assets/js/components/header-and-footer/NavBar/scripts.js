function scripts() {
  const componentList = document.getElementsByClassName('NavBar');

  if (componentList.length > 0) {
    for (let i = 0; i < componentList.length; i++) {
      const component = componentList[i];
      const mobileTrigger = component.getElementsByClassName('js-mobileTrigger')[0];
      const closeTrigger = component.getElementsByClassName('js-closeIcon')[0];
      const mobileShow = component.getElementsByClassName('js-mobileShow')[0];
      const modalCover = component.getElementsByClassName('js-modalCover')[0];

      const openMobile = () => {
        mobileShow.classList.add('is-active');
        modalCover.classList.add('is-active');
        document.body.classList.add('has-overlay');
      };

      const closeMobile = () => {
        mobileShow.classList.remove('is-active');
        modalCover.classList.remove('is-active');
        document.body.classList.remove('has-overlay');
      };

      mobileTrigger.addEventListener('click', openMobile);
      closeTrigger.addEventListener('click', closeMobile);
      modalCover.addEventListener('click', closeMobile);

      window.componentInterfaces.NavBar = [
        ...(window.componentInterfaces.NavBar || []),
        {
          methods: {
            closeMobile,
          },
          node: component,
        },
      ];
    }
  }
}


export default scripts();
