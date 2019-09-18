import initComponents from './../../../utilities/js/helpers/initComponents.js';
import getProp from './../../../utilities/js/helpers/getProp.js';


function scripts() {
  const enhanceInstance = (node) => {
    const discourseEmbedUrl = getProp('url', node);

    window.DiscourseEmbed = {
      discourseUrl: 'https://discussions.vulekamali.gov.za/',
      discourseEmbedUrl,
    };

    /* eslint-disable */
    (function() {
      var d = document.createElement('script');
      d.type = 'text/javascript';
      d.async = true;
      d.src = DiscourseEmbed.discourseUrl + 'javascripts/embed.js';
      (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(d);
    })();
    /* eslint-enable */
  };

  initComponents('Comments', enhanceInstance);
}


export default scripts();
