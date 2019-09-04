import jan from './jan.html';
import feb from './feb.html';
import mar from './mar.html';
import apr from './apr.html';
import may from './may.html';
import jun from './jun.html';
import jul from './jul.html';
import aug from './aug.html';
import sep from './sep.html';
import oct from './oct.html';
import nov from './nov.html';
import dec from './dec.html';


export default function returnHtml(key) {
  switch (key) {
    case 'January': return jan;
    case 'February': return feb;
    case 'March': return mar;
    case 'April': return apr;
    case 'May': return may;
    case 'June': return jun;
    case 'July': return jul;
    case 'August': return aug;
    case 'September': return sep;
    case 'October': return oct;
    case 'November': return nov;
    case 'December': return dec;
    default: return '';
  }
}
