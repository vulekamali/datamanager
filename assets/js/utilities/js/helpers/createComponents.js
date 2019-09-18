export default function createComponents(nameString, callback) {
  const nodesList = document.querySelectorAll(`[data-create-component="${nameString}"]`);

  for (let i = 0; i < nodesList.length; i++) {
    const node = nodesList[i];
    callback(node);
  }
}
