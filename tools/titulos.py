#!/usr/bin/env python3
"""Traducción española de los títulos de los días (cabecera del oficio).
Añade a cada día de data/m-*.json los campos "te" (título), "vte" (título de las
I Vísperas del día siguiente) y "tpe" (día del Tiempo que se conmemora).
Criterios, los mismos de las conmemoraciones ya traducidas en trad/03 y trad/04:
«feria II de la I semana de Adviento», «domingo XIII después de Pentecostés
(III domingo de agosto)», «día II de la octava de Navidad», «Santísima Virgen María».
Si el título latino coincide con una conmemoración ya traducida («Commemoratio …»),
se toma de allí. Ferias, domingos y días de octava, por regla; fiestas y santos,
por la tabla FIX. Un título sin traducción se avisa y queda sólo en latín.
Idempotente. Uso: titulos.py <raiz_app>"""
import re, json, glob, os

ROM = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,'XI':11,'XII':12,'XIII':13,'XIV':14,
       'XV':15,'XVI':16,'XVII':17,'XVIII':18,'XIX':19,'XX':20,'XXI':21,'XXII':22,'XXIII':23,'XXIV':24}
RN = {v: k for k, v in ROM.items()}
WORD = {'secunda':2,'tertia':3,'quarta':4,'quinta':5,'sexta':6,'septima':7,'octava':8,'nona':9,'decima':10,'undecima':11,'duodecima':12}
MES = {'Januarii':'enero','Februarii':'febrero','Martii':'marzo','Aprilis':'abril','Maji':'mayo','Junii':'junio','Julii':'julio',
       'Augusti':'agosto','Septembris':'septiembre','Octobris':'octubre','Novembris':'noviembre','Decembris':'diciembre'}

def num(w):
    """Número romano o latino → romano."""
    if w in ROM: return w
    n = WORD.get(w.lower())
    return RN[n] if n else None

def semana(s):
    s = s.strip()
    m = re.fullmatch(r'(\w+) Adventus', s)
    if m and num(m.group(1)): return f'de la {num(m.group(1))} semana de Adviento'
    m = re.fullmatch(r'(\w+) in Quadragesima', s)
    if m and num(m.group(1)): return f'de la {num(m.group(1))} semana de Cuaresma'
    m = re.fullmatch(r'(\w+) post Epiphaniam', s, re.I)
    if m and num(m.group(1)): return f'de la {num(m.group(1))} semana después de Epifanía'
    m = re.fullmatch(r'(\w+) post Octavam (Pentecostes|Paschæ)', s, re.I)
    if m and num(m.group(1)):
        return f'de la {num(m.group(1))} semana después de la octava de ' + ('Pentecostés' if m.group(2) == 'Pentecostes' else 'Pascua')
    return {'Septuagesimæ':'de la semana de Septuagésima','Sexagesimæ':'de la semana de Sexagésima',
            'Quinquagesimæ':'de la semana de Quincuagésima','Passionis':'de la semana de Pasión',
            'post Ascensionem':'de la semana después de la Ascensión'}.get(s)

def mes(t, que):
    """«… III. Augusti» → (resto, ' (III semana|domingo de agosto)')."""
    m = re.search(r'\s+([IV]+)\.\s+(\w+)$', t)
    if m and m.group(2) in MES:
        return t[:m.start()], f' ({m.group(1)} {que} de {MES[m.group(2)]})'
    return t, ''

TEMP = {'Adventus':'de Adviento','Quadragesimæ':'de Cuaresma','Pentecostes':'de Pentecostés','Septembris':'de septiembre'}

def regla(t):
    if t.startswith('Dominica'):
        t, suf = mes(t, 'domingo')
        m = re.fullmatch(r'Dominica (\w+) (Adventus|in Quadragesima|Post Epiphaniam|Post Pascha|Post Pentecosten|Passionis)', t, re.I)
        if m and num(m.group(1)):
            tt = {'adventus':'de Adviento','in quadragesima':'de Cuaresma','post epiphaniam':'después de Epifanía',
                  'post pascha':'después de Pascua','post pentecosten':'después de Pentecostés','passionis':'de Pasión'}[m.group(2).lower()]
            return f'Domingo {num(m.group(1))} {tt}{suf}'
        m = re.fullmatch(r'Dominica (\w+) et Ultima Post Pentecosten', t, re.I)
        if m and num(m.group(1)): return f'Domingo {num(m.group(1))} y último después de Pentecostés{suf}'
        return None
    t, suf = mes(t, 'semana')
    m = re.fullmatch(r'Feria (\w+) infra Hebdomadam (.+)', t)
    if m and num(m.group(1)) and semana(m.group(2)): return f'Feria {num(m.group(1))} {semana(m.group(2))}{suf}'
    m = re.fullmatch(r'Sabbato infra Hebdomadam (.+)', t)
    if m and semana(m.group(1)): return f'Sábado {semana(m.group(1))}{suf}'
    m = re.fullmatch(r'Feria (\w+) post Ascensionem', t)
    if m and num(m.group(1)): return f'Feria {num(m.group(1))} después de la Ascensión'
    m = re.fullmatch(r'Feria (\w+) Quattuor Temporum (\w+)', t)
    if m and num(m.group(1)) and m.group(2) in TEMP: return f'Feria {num(m.group(1))} de las Témporas {TEMP[m.group(2)]}'
    m = re.fullmatch(r'Sabbato Quattuor Temporum (\w+)', t)
    if m and m.group(1) in TEMP: return f'Sábado de las Témporas {TEMP[m.group(1)]}'
    m = re.fullmatch(r'Feria (\w+) Hebdomadæ Sanctæ', t)
    if m and num(m.group(1)): return f'Feria {num(m.group(1))} de la Semana Santa'
    m = re.fullmatch(r'Feria (\w+) in Rogationibus', t)
    if m and num(m.group(1)): return f'Feria {num(m.group(1))} de Rogativas'
    m = re.fullmatch(r'Feria (\w+) post Cineres', t)
    if m and num(m.group(1)): return f'Feria {num(m.group(1))} después de Ceniza'
    if t == 'Sabbato post Cineres': return 'Sábado después de Ceniza'
    m = re.fullmatch(r'Dies? (\w+) infra octavam (Paschæ|Pentecostes)', t, re.I)
    if m and num(m.group(1)): return f'Día {num(m.group(1))} de la octava de ' + ('Pascua' if m.group(2) == 'Paschæ' else 'Pentecostés')
    m = re.fullmatch(r'Diei (\w+) infra Octavam Nativitatis', t)
    if m and num(m.group(1)): return f'Día {num(m.group(1))} de la octava de Navidad'
    m = re.fullmatch(r'Dies? (\w+) Januarii', t)
    if m and num(m.group(1)): return f'Día {ROM[num(m.group(1))]} de enero'
    return None

FIX = {
 # Temporal
 'Commemoratio Baptismatis Domini Nostri Jesu Christi':'Conmemoración del Bautismo de nuestro Señor Jesucristo',
 'Domini Nostri Jesu Christi Regis':'Nuestro Señor Jesucristo Rey',
 'Die Octavæ Nativitatis Domini':'Día de la Octava de la Natividad del Señor',
 'Dominica Infra Octavam Nativitatis':'Domingo de la octava de Navidad',
 'Dominica Pentecostes':'Domingo de Pentecostés',
 'Dominica Resurrectionis':'Domingo de Resurrección',
 'Dominica Sanctissimæ Trinitatis':'Domingo de la Santísima Trinidad',
 'Dominica II Passionis seu in Palmis':'Domingo segundo de Pasión o de Ramos',
 'Dominica in Albis in Octava Paschæ':'Domingo in Albis, Octava de Pascua',
 'Dominica in Quinquagesima':'Domingo de Quincuagésima',
 'Dominica in Septuagesima':'Domingo de Septuagésima',
 'Dominica in Sexagesima':'Domingo de Sexagésima',
 'Dominica post Ascensionem':'Domingo después de la Ascensión',
 'Feria IV Cinerum':'Miércoles de Ceniza',
 'Feria Quinta in Cena Domini':'Jueves de la Cena del Señor',
 'Feria Sexta in Passione et Morte Domini':'Viernes de la Pasión y Muerte del Señor',
 'Sabbato Sancto':'Sábado Santo',
 'Sabbato in Albis':'Sábado in Albis',
 'Sabbato in Vigilia Pentecostes':'Sábado, Vigilia de Pentecostés',
 'Festum Sanctissimi Corporis Christi':'Fiesta del Santísimo Cuerpo de Cristo',
 'Sacratissimi Cordis Domini Nostri Jesu Christi':'Sacratísimo Corazón de nuestro Señor Jesucristo',
 'Pretiosissimi Sanguinis Domini Nostri Jesu Christi':'Preciosísima Sangre de nuestro Señor Jesucristo',
 'Sanctissimi Nominis Jesu':'Santísimo Nombre de Jesús',
 'Sanctæ Familiæ Jesu Mariæ Joseph':'Sagrada Familia de Jesús, María y José',
 'In Ascensione Domini':'Ascensión del Señor',
 'In Epiphania Domini':'Epifanía del Señor',
 'In Nativitate Domini':'Natividad del Señor',
 'In Transfiguratione Domini Nostri Jesu Christi':'Transfiguración de nuestro Señor Jesucristo',
 'In Vigilia Ascensionis':'Vigilia de la Ascensión',
 'In Vigilia Nativitatis Domini':'Vigilia de la Natividad del Señor',
 'In Exaltatione Sanctæ Crucis':'Exaltación de la Santa Cruz',
 'In Commemoratione Omnium Fidelium Defunctorum':'Conmemoración de todos los Fieles Difuntos',
 'Omnium Sanctorum':'Todos los Santos',
 # Santísima Virgen
 'Beatæ Mariæ Virginis Reginæ':'Santísima Virgen María Reina',
 'Beatæ Mariæ Virginis a Rosario':'Santísima Virgen María del Rosario',
 'Immaculati Cordis Beatæ Mariæ Virginis':'Inmaculado Corazón de la Santísima Virgen María',
 'In Annuntiatione Beatæ Mariæ Virginis':'Anunciación de la Santísima Virgen María',
 'In Apparitione Beatæ Mariæ Virginis Immaculatæ':'Aparición de la Santísima Virgen María Inmaculada',
 'In Assumptione Beatæ Mariæ Virginis':'Asunción de la Santísima Virgen María',
 'In Conceptione Immaculata Beatæ Mariæ Virginis':'Inmaculada Concepción de la Santísima Virgen María',
 'In Nativitate Beatæ Mariæ Virginis':'Natividad de la Santísima Virgen María',
 'In Præsentatione Beatæ Mariæ Virginis':'Presentación de la Santísima Virgen María',
 'In Purificatione Beatæ Mariæ Virginis':'Purificación de la Santísima Virgen María',
 'In Visitatione Beatæ Mariæ Virginis':'Visitación de la Santísima Virgen María',
 'In Vigilia Assumptionis B.M.V.':'Vigilia de la Asunción de la Santísima Virgen María',
 'Maternitatis Beatæ Mariæ Virginis':'Maternidad de la Santísima Virgen María',
 'S. Nominis Beatæ Mariæ Virginis':'Santo Nombre de la Santísima Virgen María',
 'Sanctæ Mariæ Sabbato':'Santa María en sábado',
 'Sanctæ Mariæ Virginis ad Nives':'Santa María Virgen de las Nieves',
 'Septem Dolorum Beatæ Mariæ Virginis':'Siete Dolores de la Santísima Virgen María',
 'Ss. Septem Fundatorum Ordinis Servorum B. M. V.':'Siete santos Fundadores de la Orden de los Siervos de la Santísima Virgen María',
 # Dedicaciones, ángeles, apóstoles
 'In Cathedra S. Petri Apostoli':'Cátedra de san Pedro Apóstol',
 'In Commemoratione S. Pauli Apostoli':'Conmemoración de san Pablo Apóstol',
 'In Conversione S. Pauli Apostoli':'Conversión de san Pablo Apóstol',
 'In Decollatione S. Joannis Baptistæ':'Degollación de san Juan Bautista',
 'In Dedicatione Archibasilicæ Ss. Salvatoris':'Dedicación de la Archibasílica del Santísimo Salvador',
 'In Dedicatione Basilicarum Ss. Apostolorum Petri et Pauli':'Dedicación de las basílicas de los santos Apóstoles Pedro y Pablo',
 'In Dedicatione S. Michaëlis Archangelis':'Dedicación de san Miguel Arcángel',
 'In Nativitate S. Joannis Baptistæ':'Natividad de san Juan Bautista',
 'In Vigilia S. Joannis Baptistæ':'Vigilia de san Juan Bautista',
 'In Vigilia S. Laurentii Mart.':'Vigilia de san Lorenzo, Mártir',
 'In Vigilia Ss. Petri et Pauli Apostolorum':'Vigilia de los santos Apóstoles Pedro y Pablo',
 'S. Raphaëlis Archangeli':'San Rafael Arcángel',
 'Ss. Angelorum Custodum':'Santos Ángeles Custodios',
 'SS. Apostolorum Petri et Pauli':'Santos Apóstoles Pedro y Pablo',
 'S. Andreæ Apostoli':'San Andrés Apóstol',
 'S. Barnabæ Apostoli':'San Bernabé Apóstol',
 'S. Bartholomæi Apostoli':'San Bartolomé Apóstol',
 'S. Jacobi Apostoli':'Santiago Apóstol',
 'S. Joannis Apostoli et Evangelistæ':'San Juan, Apóstol y Evangelista',
 'S. Lucæ Evangelistæ':'San Lucas Evangelista',
 'S. Marci Evangelistæ':'San Marcos Evangelista',
 'S. Matthiæ Apostoli':'San Matías Apóstol',
 'S. Matthæi Apostoli et Evangelistæ':'San Mateo, Apóstol y Evangelista',
 'S. Thomæ Apostoli':'Santo Tomás Apóstol',
 'Ss. Philippi et Jacobi Apostolorum':'Santos Felipe y Santiago, Apóstoles',
 'Ss. Simonis et Judæ Apostolorum':'Santos Simón y Judas, Apóstoles',
 'S. Stephani Protomartyris':'San Esteban, Protomártir',
 'Ss. Innocentium':'Santos Inocentes',
 # Santos
 'S. Agathæ Virginis et Martyris':'Santa Águeda, Virgen y Mártir',
 'S. Agnetis Virginis et Martyris':'Santa Inés, Virgen y Mártir',
 'S. Alberti Magni Episcopi Confessoris et Ecclesiæ Doctoris':'San Alberto Magno, Obispo, Confesor y Doctor de la Iglesia',
 'S. Alfonsi Mariæ de Ligorio Episcopi Confessoris et Ecclesiæ Doctoris':'San Alfonso María de Ligorio, Obispo, Confesor y Doctor de la Iglesia',
 'S. Aloisii Gonzagæ Confessoris':'San Luis Gonzaga, Confesor',
 'S. Ambrosii Episcopi Confessoris et Ecclesiæ Doctoris':'San Ambrosio, Obispo, Confesor y Doctor de la Iglesia',
 'S. Andreæ Avellini Confessoris':'San Andrés Avelino, Confesor',
 'S. Andreæ Corsini Episcopi et Confessoris':'San Andrés Corsini, Obispo y Confesor',
 'S. Angelæ Mericiæ Virginis':'Santa Ángela Merici, Virgen',
 'S. Annæ Matris B.M.V.':'Santa Ana, Madre de la Santísima Virgen María',
 'S. Anselmi Episcopi Confessoris et Ecclesiæ Doctoris':'San Anselmo, Obispo, Confesor y Doctor de la Iglesia',
 'S. Antonii Abbatis':'San Antonio, Abad',
 'S. Antonii Mariæ Claret Episcopi et Confessoris':'San Antonio María Claret, Obispo y Confesor',
 'S. Antonii Mariæ Zaccaria Confessoris':'San Antonio María Zaccaria, Confesor',
 'S. Antonii de Padua Confessoris et Ecclesiæ Doctoris':'San Antonio de Padua, Confesor y Doctor de la Iglesia',
 'S. Antonini Episcopi et Confessoris':'San Antonino, Obispo y Confesor',
 'S. Apollinaris Episcopi et Martyris':'San Apolinar, Obispo y Mártir',
 'S. Athanasii Episcopi Confessoris et Ecclesiæ Doctoris':'San Atanasio, Obispo, Confesor y Doctor de la Iglesia',
 'S. Augustini Episcopi et Confessoris':'San Agustín, Obispo y Confesor',
 'S. Augustini Episcopi et Confessoris et Ecclesiæ Doctoris':'San Agustín, Obispo, Confesor y Doctor de la Iglesia',
 'S. Basilii Magni, Episcopis Confessoris et Ecclesiæ Doctoris':'San Basilio Magno, Obispo, Confesor y Doctor de la Iglesia',
 'S. Bedæ Venerabilis Confessoris et Ecclesiæ Doctoris':'San Beda el Venerable, Confesor y Doctor de la Iglesia',
 'S. Bernardi Abbatis et Ecclesiæ Doctoris':'San Bernardo, Abad y Doctor de la Iglesia',
 'S. Bernardini Senensis Confessoris':'San Bernardino de Siena, Confesor',
 'S. Bibianæ Virginis et Martyris':'Santa Bibiana, Virgen y Mártir',
 'S. Birgittæ Viduæ':'Santa Brígida, Viuda',
 'S. Bonaventuræ Episcopi Confessoris et Ecclesiæ Doctoris':'San Buenaventura, Obispo, Confesor y Doctor de la Iglesia',
 'S. Bonifatii Episcopi et Martyris':'San Bonifacio, Obispo y Mártir',
 'S. Brunonis Confessoris':'San Bruno, Confesor',
 'S. Cajetani Confessoris':'San Cayetano, Confesor',
 'S. Callisti Papæ et Martyris':'San Calixto, Papa y Mártir',
 'S. Camilli de Lellis Confessoris':'San Camilo de Lelis, Confesor',
 'S. Caroli Episcopi et Confessoris':'San Carlos, Obispo y Confesor',
 'S. Catharinæ Senensis Virginis':'Santa Catalina de Siena, Virgen',
 'S. Catharinæ Virginis et Martyris':'Santa Catalina, Virgen y Mártir',
 'S. Claræ Virginis':'Santa Clara, Virgen',
 'S. Clementis Papæ et Martyris':'San Clemente, Papa y Mártir',
 'S. Cyrilli Episc. Alexandrini Confessoris et Ecclesiæ Doctoris':'San Cirilo, Obispo de Alejandría, Confesor y Doctor de la Iglesia',
 'S. Cæciliæ Virginis et Martyris':'Santa Cecilia, Virgen y Mártir',
 'S. Damasi Papæ et Confessoris':'San Dámaso, Papa y Confesor',
 'S. Didaci Confessoris':'San Diego, Confesor',
 'S. Dominici Confessoris':'Santo Domingo, Confesor',
 'S. Eduardi Regis Confessoris':'San Eduardo, Rey y Confesor',
 'S. Elisabeth Reg. Portugaliæ Viduæ':'Santa Isabel, Reina de Portugal, Viuda',
 'S. Elisabeth Viduæ':'Santa Isabel, Viuda',
 'S. Ephræm Syri Confessoris et Ecclesiæ Doctoris':'San Efrén Sirio, Confesor y Doctor de la Iglesia',
 'S. Eusebii Episcopi et Martyris':'San Eusebio, Obispo y Mártir',
 'S. Felicis de Valois Confessoris':'San Félix de Valois, Confesor',
 'S. Fidelis de Sigmaringa Martyris':'San Fidel de Sigmaringa, Mártir',
 'S. Francisci Caracciolo Confessoris':'San Francisco Caracciolo, Confesor',
 'S. Francisci de Paula Confessoris':'San Francisco de Paula, Confesor',
 'S. Leonis I Papæ Confessoris et Ecclesiæ Doctoris':'San León I, Papa, Confesor y Doctor de la Iglesia',
 'S. Norberti Episcopi et Confessoris':'San Norberto, Obispo y Confesor',
 'Ss. Mauritii et Sociorum Martyrum':'Santos Mauricio y Compañeros, Mártires',
 'S. Francisci Borgiæ Confessoris':'San Francisco de Borja, Confesor',
 'S. Francisci Confessoris':'San Francisco, Confesor',
 'S. Francisci Salesii Episcopi Confessoris et Ecclesiæ Doctoris':'San Francisco de Sales, Obispo, Confesor y Doctor de la Iglesia',
 'S. Francisci Xaverii Confessoris':'San Francisco Javier, Confesor',
 'S. Gabrielis a Virgine Perdolente Confessoris':'San Gabriel de la Dolorosa, Confesor',
 'S. Gertrudis Virginis':'Santa Gertrudis, Virgen',
 'S. Gregorii Barbadici Episcopi et Confessoris':'San Gregorio Barbarigo, Obispo y Confesor',
 'S. Gregorii Nazianzeni Episcopi Confessoris et Ecclesiæ Doctoris':'San Gregorio Nacianceno, Obispo, Confesor y Doctor de la Iglesia',
 'S. Gregorii Thaumaturgi Episcopi et Confessoris':'San Gregorio Taumaturgo, Obispo y Confesor',
 'S. Gregorii VII Papæ et Confessoris':'San Gregorio VII, Papa y Confesor',
 'S. Gulielmi Abbatis':'San Guillermo, Abad',
 'S. Hedwigis Viduæ':'Santa Eduviges, Viuda',
 'S. Henrici Imperatoris Confessoris':'San Enrique, Emperador y Confesor',
 'S. Hermenegildi Martyris':'San Hermenegildo, Mártir',
 'S. Hieronymi Presbyteris Confessoris et Ecclesiæ Doctoris':'San Jerónimo, Presbítero, Confesor y Doctor de la Iglesia',
 'S. Hieronymi Æmiliani Confessoris':'San Jerónimo Emiliani, Confesor',
 'S. Hilarii Episcopi Confessoris Ecclesiæ Doctoris':'San Hilario, Obispo, Confesor y Doctor de la Iglesia',
 'S. Hyacinthi Confessoris':'San Jacinto, Confesor',
 'S. Ignatii Confessoris':'San Ignacio, Confesor',
 'S. Ignatii Episcopi et Martyris':'San Ignacio, Obispo y Mártir',
 'S. Irenæi Episcopi et Martyris':'San Ireneo, Obispo y Mártir',
 'S. Januarii Episcopi et Sociorum Martyrum':'San Jenaro, Obispo, y sus Compañeros, Mártires',
 'S. Joachim Confessoris, Patris B. M. V.':'San Joaquín, Confesor, Padre de la Santísima Virgen María',
 'S. Joannis Baptistæ de la Salle Confessoris':'San Juan Bautista de La Salle, Confesor',
 'S. Joannis Bosco Confessoris':'San Juan Bosco, Confesor',
 'S. Joannis Cantii Confessoris':'San Juan Cancio, Confesor',
 'S. Joannis Chrysostomi Episcopi Confessoris et Ecclesiæ Doctoris':'San Juan Crisóstomo, Obispo, Confesor y Doctor de la Iglesia',
 'S. Joannis Eudes Confessoris':'San Juan Eudes, Confesor',
 'S. Joannis Gualberti Abbatis':'San Juan Gualberto, Abad',
 'S. Joannis Leonardi Confessoris':'San Juan Leonardi, Confesor',
 'S. Joannis Mariæ Vianney Confessoris':'San Juan María Vianney, Confesor',
 'S. Joannis a Cruce Confessoris et Ecclesiæ Doctoris':'San Juan de la Cruz, Confesor y Doctor de la Iglesia',
 'S. Joannis a S. Facundo Confessoris':'San Juan de Sahagún, Confesor',
 'S. Joannis de Matha Confessoris':'San Juan de Mata, Confesor',
 'S. Joannæ Franciscæ Frémiot de Chantal Viduæ':'Santa Juana Francisca Frémiot de Chantal, Viuda',
 'S. Josaphat Episcopi et Martyris':'San Josafat, Obispo y Mártir',
 'S. Joseph Opificis':'San José Obrero',
 'S. Joseph Sponsi B.M.V. Confessoris':'San José, Esposo de la Santísima Virgen María, Confesor',
 'S. Josephi Calasanctii Confessoris':'San José de Calasanz, Confesor',
 'S. Josephi de Cupertino Confessoris':'San José de Cupertino, Confesor',
 'S. Julianæ de Falconeriis Virginis':'Santa Juliana Falconieri, Virgen',
 'S. Justini Martyris':'San Justino, Mártir',
 'S. Laurentii Justiniani Episcopi et Confessoris':'San Lorenzo Justiniano, Obispo y Confesor',
 'S. Laurentii Martyris':'San Lorenzo, Mártir',
 'S. Laurentii a Brundusio Confessoris et Ecclesiæ Doctoris':'San Lorenzo de Brindis, Confesor y Doctor de la Iglesia',
 'S. Lini Papæ et Martyris':'San Lino, Papa y Mártir',
 'S. Luciæ Virginis et Martyris':'Santa Lucía, Virgen y Mártir',
 'S. Ludovici Regis Franciæ Confessoris':'San Luis, Rey de Francia, Confesor',
 'S. Marcelli Papæ et Martyris':'San Marcelo, Papa y Mártir',
 'S. Margaritæ Mariæ Alacoque Virginis':'Santa Margarita María Alacoque, Virgen',
 'S. Margaritæ Reginæ Viduæ':'Santa Margarita, Reina, Viuda',
 'S. Mariæ Magdalenæ Pœnitentis':'Santa María Magdalena, Penitente',
 'S. Mariæ Magdalenæ de Pazzis Virginis':'Santa María Magdalena de Pazzi, Virgen',
 'S. Marthæ Virginis':'Santa Marta, Virgen',
 'S. Martini Episcopi et Confessoris':'San Martín, Obispo y Confesor',
 'S. Martini Papæ et Martyris':'San Martín, Papa y Mártir',
 'S. Martinæ Virginis et Martyris':'Santa Martina, Virgen y Mártir',
 'S. Monicæ Viduæ':'Santa Mónica, Viuda',
 'S. Nicolai Episcopi et Confessoris':'San Nicolás, Obispo y Confesor',
 'S. Nicolai de Tolentino Confessoris':'San Nicolás de Tolentino, Confesor',
 'S. Paschalis Baylon Confessoris':'San Pascual Bailón, Confesor',
 'S. Pauli Primi Eremitæ et Confessoris':'San Pablo, primer Ermitaño y Confesor',
 'S. Pauli a Cruce Confessoris':'San Pablo de la Cruz, Confesor',
 'S. Paulini Episcopi et Confessoris':'San Paulino, Obispo y Confesor',
 'S. Petri Canisii Confessoris et Ecclesiæ Doctoris':'San Pedro Canisio, Confesor y Doctor de la Iglesia',
 'S. Petri Celestini Papæ et Confessoris':'San Pedro Celestino, Papa y Confesor',
 'S. Petri Chrysologi Episcopi Confessoris et Ecclesiæ Doctoris':'San Pedro Crisólogo, Obispo, Confesor y Doctor de la Iglesia',
 'S. Petri Damiani Episcopi Confessoris et Ecclesiæ Doctoris':'San Pedro Damián, Obispo, Confesor y Doctor de la Iglesia',
 'S. Petri Martyris':'San Pedro, Mártir',
 'S. Petri Nolasci Confessoris':'San Pedro Nolasco, Confesor',
 'S. Petri de Alcantara Confessoris':'San Pedro de Alcántara, Confesor',
 'S. Philippi Benitii Confessoris':'San Felipe Benicio, Confesor',
 'S. Philippi Neri Confessoris':'San Felipe Neri, Confesor',
 'S. Pii V Papæ et Confessoris':'San Pío V, Papa y Confesor',
 'S. Pii X Papæ Confessoris':'San Pío X, Papa y Confesor',
 'S. Polycarpi Episcopi et Martyris':'San Policarpo, Obispo y Mártir',
 'S. Raymundi Nonnati Confessoris':'San Ramón Nonato, Confesor',
 'S. Raymundi de Peñafort Confessoris':'San Raimundo de Peñafort, Confesor',
 'S. Roberti Bellarmino Episcopi Confessoris et Ecclesiæ Doctoris':'San Roberto Belarmino, Obispo, Confesor y Doctor de la Iglesia',
 'S. Romualdi Abbatis':'San Romualdo, Abad',
 'S. Rosæ a Sancta Maria Limanæ Virginis':'Santa Rosa de Santa María de Lima, Virgen',
 'S. Scholasticæ Virginis':'Santa Escolástica, Virgen',
 'S. Silvestri Abbatis':'San Silvestre, Abad',
 'S. Stanislai Episcopi et Martyris':'San Estanislao, Obispo y Mártir',
 'S. Stephani Hungariæ Regis Confessoris':'San Esteban, Rey de Hungría, Confesor',
 'S. Teresiæ Virginis':'Santa Teresa, Virgen',
 'S. Theresiæ a Jesu Infante Virginis':'Santa Teresa del Niño Jesús, Virgen',
 'S. Timothei Episcopi et Martyris':'San Timoteo, Obispo y Mártir',
 'S. Titi Episcopi et Confessoris':'San Tito, Obispo y Confesor',
 'S. Ubaldi Episcopi et Confessoris':'San Ubaldo, Obispo y Confesor',
 'S. Venantii Martyris':'San Venancio, Mártir',
 'S. Vincentii a Paulo Confessoris':'San Vicente de Paúl, Confesor',
 'S. Wenceslai Ducis et Martyris':'San Wenceslao, Duque y Mártir',
 'SS. Cleti et Marcellini Summorum Pontificum et Martyrum':'Santos Cleto y Marcelino, Sumos Pontífices y Mártires',
 'SS. Soteris et Caii Summorum Pontificum et Martyrum':'Santos Sotero y Cayo, Sumos Pontífices y Mártires',
 'Ss. Cornelii Papæ et Cypriani Episcopi, Martyrum':'Santos Cornelio, Papa, y Cipriano, Obispo, Mártires',
 'Ss. Cosmæ et Damiani Martyrum':'Santos Cosme y Damián, Mártires',
 'Ss. Cyrilli et Methodii Pont. et Conf.':'Santos Cirilo y Metodio, Obispos y Confesores',
 'Ss. Fabiani et Sebastiani Martyrum':'Santos Fabián y Sebastián, Mártires',
 'Ss. Joannis et Pauli Martyrum':'Santos Juan y Pablo, Mártires',
 'Ss. Nazarii et Celsi Martyrum, Victoris I Papæ et Martyris ac Innocentii I Papæ et Confessoris':'Santos Nazario y Celso, Mártires, Víctor I, Papa y Mártir, e Inocencio I, Papa y Confesor',
 'Ss. Nerei, Achillei et Domitillæ Virg. atque Pancratii Martyrum':'Santos Nereo, Aquileo, Domitila, Virgen, y Pancracio, Mártires',
 'Ss. Septem Fratrum Martyrum, ac Rufinæ et Secundæ Virginum et Martyrum':'Santos siete Hermanos, Mártires, y santas Rufina y Segunda, Vírgenes y Mártires',
 'Ss. Vincentii et Anastasii Martyrum':'Santos Vicente y Anastasio, Mártires',
}

def _k(t):
    return re.sub(r'\s+', ' ', t.replace('J', 'I').replace('j', 'i')).strip()

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
COMM = {}   # conmemoraciones ya traducidas: latín normalizado → título español
for _f in glob.glob(os.path.join(_ROOT, 'trad', '*.json')):
    if _f.endswith('glosario.json'): continue
    for _d in ('lineas', 'html', 'mariano'):
        for _a, _b in json.load(open(_f, encoding='utf-8')).get(_d, {}).items():
            if _a.startswith('Commemoratio ') and _b.startswith('Conmemoración '):
                _t = re.sub(r'^Conmemoración (?:del |de la |de los |de las |de )', '', _b)
                COMM[_k(_a[13:])] = _t[0].upper() + _t[1:]
FIXK = {_k(a): b for a, b in FIX.items()}

def es(t):
    for a, b in (('Commemoratio: ', 'Conmemoración: '), ('Commemoratio ad Laudes tantum: ', 'Conmemoración sólo en Laudes: ')):
        if t.startswith(a):
            r = es(t[len(a):])
            return b + r if r else None
    k = _k(t)
    return COMM.get(k) or FIXK.get(k) or regla(t)

ART = [(r'^(Feria|Vigilia|Octava|Impresión|Natividad|Asunción|Anunciación|Aparición|Inmaculada|Presentación|Purificación|Visitación|'
        r'Maternidad|Transfiguración|Ascensión|Epifanía|Exaltación|Conversión|Cátedra|Degollación|Dedicación|Santísima|'
        r'Sagrada|Preciosísima|Fiesta|Conmemoración|Conversión)\b', 'de la '),
       (r'^(Domingo|Sábado|Día|Inmaculado|Sacratísimo|Santísimo|Santo Nombre)\b', 'del '),
       (r'^(Santos|Siete|Todos)\b', 'de los '), (r'^(Santas)\b', 'de las '), (r'^(San|Santa|Santo|Santiago)\b', 'de ')]

def conmemoracion(lat):
    """«Commemoratio X» → «Conmemoración de(l) …», con los mismos criterios."""
    t = es(lat[13:])
    if not t: return None
    for rx, art in ART:
        if re.match(rx, t):
            if art == 'de los ' and t.startswith('Todos'): return 'Conmemoración de ' + t
            low = t[0].lower() + t[1:] if re.match(r'^(Feria|Domingo|Sábado|Día|San|Santa|Santo|Santos|Santas|Siete santos)\b', t) and not t.startswith('Santo Nombre') else t
            return 'Conmemoración ' + art + low
    return None

if __name__ == '__main__':
    import sys
    R = sys.argv[1] if len(sys.argv) > 1 else '.'
    falta = set()
    for f in sorted(glob.glob(os.path.join(R, 'data', 'm-*.json'))):
        m = json.load(open(f, encoding='utf-8'))
        for v in m.values():
            for k, kk in (('title', 'te'), ('vt', 'vte'), ('tp', 'tpe')):
                v.pop(kk, None)
                if v.get(k):
                    la = v[k].split(' ~ ')[0]
                    t = es(la)
                    if t: v[kk] = t
                    else: falta.add(la)
        json.dump(m, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('títulos sin traducir:', len(falta)); [print('  ', t) for t in sorted(falta)]
