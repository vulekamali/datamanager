export default function escapeRegExp(text) {
  return text.replace(/[\/\-\[\\\]\{\}\(\)\*\+\?\.\,\^\$\#\s]/gi, '\\$&');
}
