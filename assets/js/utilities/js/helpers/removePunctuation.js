export default function removePunctuation(string) {
  return string.replace(/[^\w\s]/g, ' ');
}
