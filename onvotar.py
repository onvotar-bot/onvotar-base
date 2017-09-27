import re
import sys
import logging

from calculate import calculate

logger = logging.getLogger('on_votar')

_DNI_LETTERS = 'TRWAGMYFPDXBNJZSQVHLCKEO'
_DNI_PATTERN = re.compile('^([0-9]{8}[^A-Z]?[A-Z])$')
_DOB_PATTERN = re.compile('^([0-9]{8})$')
_ZIP_PATTERN = re.compile('^([0-9]{5})$')

DEFAULT_ERR = (
    'Per conèixer el teu col·legi electoral, '
    'envia un missatge amb les teves dades '
    'separades per espais i '
    'fent servir aquest format: \n'
    'DNI DATA_NAIXEMENT CODI_POSTAL\n\n'
    'Exemple:\n00001714N 01/10/2017 01234'
)

DATA_DISCLAIMER = (
    'Aquest bot utilitza la mateixa tecnologia que '
    'la web original oficial del Referèndum.\n'
    'No desa ni mostra als autors cap dada sensible.'
)


def answer(text):
    try:
        dni, date, cp = _check_input_data(text)
    except ValueError as e:
        res = str(e)
        if res == DEFAULT_ERR:
            logger.info('Error: No hi ha 3 dades')
        else:
            logger.info('Error: %s', res)
    else:
        result = calculate(dni, date, cp)
        if result:
            res = (
                '{}\n{}\n{}\n\n'
                'Districte: {}\n'
                'Secció: {}\n'
                'Mesa: {}'
            ).format(*result)
            logger.info(
                'Punt de votacio retornat correctament. %s %s',
                date[:4], cp
            )
        else:
            res = (
                'Alguna de les dades entrades no és correcta.\n'
                'Revisa-les, si us plau.'
            )
            logger.info('Bon format pero dades incorrectes')
    logger.info('---')
    return res


def _check_input_data(text):
    splitted = text.split(' ')
    if len(splitted) != 3:
        raise ValueError(DEFAULT_ERR)

    raw_dni, raw_date, cp = splitted

    dni = raw_dni.upper().replace('-', '')
    match = _DNI_PATTERN.match(dni)
    if not match:
        raise ValueError('Revisa el format del DNI')

    if not _is_dni_letter_correct(dni):
        raise ValueError('La lletra del DNI no coincideix')

    date = raw_date.upper().replace('/', '')
    match = _DOB_PATTERN.match(date)
    if not match:
        raise ValueError('Revisa el format de la data de naixement')
    date = date[-4:]+date[2:4]+date[:2]

    match = _ZIP_PATTERN.match(cp)
    if not match:
        raise ValueError('Revisa el format del codi postal')

    return dni, date, cp


def _is_dni_letter_correct(dni):
    dni_num = int(dni[:-1])
    letter_num = int(dni_num/23)
    letter_num *= 23
    letter_num = dni_num-letter_num
    return _DNI_LETTERS[letter_num] == dni[-1]


if __name__ == '__main__':
    print(answer(' '.join(sys.argv[1:])))
