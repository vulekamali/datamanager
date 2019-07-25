import { h, render } from 'preact';
import ResponsiveChart from './index.jsx';
import getProps from './../../../utilities/js/helpers/getProp.js';


function scripts() {
  const nodesList = document.getElementsByClassName('js-initResponsiveChart');

  for (let i = 0; i < nodesList.length; i++) {
    const node = nodesList[i];
    const items = getProps('items', node, 'json');
    const type = getProps('type', node);
    const rawDownload = getProps('download', node, 'json');

    const downloadHasProps = !!(rawDownload && rawDownload.heading && rawDownload.subHeading && rawDownload.type);
    const download = downloadHasProps ? rawDownload : null;

    render(
      <ResponsiveChart {...{ items, download, type }} />,
      node,
    );
  }
}


export default scripts();
