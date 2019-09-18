export default function calcViewportPosition(node) {
  const scrollPosition = document.body.scrollTop;
  const nodeAbsolutePostion = node.offsetTop;
  return scrollPosition - nodeAbsolutePostion;
}
