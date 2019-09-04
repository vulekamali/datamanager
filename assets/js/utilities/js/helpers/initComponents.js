export default function initComponents(nameString, callback, create) {
  const type = create ? 'create' : 'enhance';
  const nodesList = document.querySelectorAll(`[data-${type}-component="${nameString}"]`);

  for (let i = 0; i < nodesList.length; i++) {
    const node = nodesList[i];
    callback(node);
  }
}
