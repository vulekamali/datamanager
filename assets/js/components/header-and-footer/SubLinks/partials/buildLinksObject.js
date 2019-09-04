export default function buildLinksObject(nodeList) {
  let result = [];

  for (let i = 0; i < nodeList.length; i++) {
    const node = nodeList[i];
    const connectedId = node.getAttribute('data-connected-id');
    if (connectedId) {
      result.push({
        target: document.getElementById(connectedId),
        link: node,
      });
    }
  }

  return result;
}
