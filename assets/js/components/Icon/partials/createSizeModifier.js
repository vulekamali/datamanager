export default function createSizeModifier(string) {
  switch (string) {
    case 'xs': return ' Icon--extraSmall';
    case 's': return ' Icon--small';
    case 'l': return ' Icon--large';
    case 'xl': return ' Icon--extraLarge';
    default: return '';
  }
}
