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


class OnVotarError(ValueError):
    def __init__(self):
        self.args = [self.text]


class No3DataError(OnVotarError):
    text = DEFAULT_ERR


class NifFormatError(OnVotarError):
    text = 'Revisa el format del DNI'


class NifLetterError(OnVotarError):
    text = 'La lletra del DNI no coincideix'


class DateFormatError(OnVotarError):
    text = 'Revisa el format de la data de naixement'


class CpFormatError(OnVotarError):
    text = 'Revisa el format del codi postal'


def answer(text):
    try:
        dni, date, cp = _check_input_data(text)
    except OnVotarError as e:
        res = str(e)
        logger.info('%s', e.__class__.__name__)
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
                'OK - %s %s',
                date[:4], cp
            )
        else:
            res = (
                'Les dades introduides no han retornat cap resultat.\n\n'
                'Si has canviat recentment de domicili, prova el'
                'codi postal anterior.\n'
                'Si tens més dubtes, contacta amb el correu electrònic'
                'oficial de la Generalitat:\n'
                'onvotar@garantiesreferendum.net'
            )
            logger.info('DADES_INCORRECTES')
    return res


def _check_input_data(text):
    splitted = text.split(' ')
    if len(splitted) != 3:
        raise No3DataError()

    raw_dni, raw_date, cp = splitted

    dni = raw_dni.upper().replace('-', '')
    match = _DNI_PATTERN.match(dni)
    if not match:
        raise NifFormatError()

    if not _is_dni_letter_correct(dni):
        raise NifLetterError()

    date = raw_date.upper().replace('/', '')
    match = _DOB_PATTERN.match(date)
    if not match:
        raise DateFormatError()
    date = date[-4:]+date[2:4]+date[:2]

    match = _ZIP_PATTERN.match(cp)
    if not match:
        raise CpFormatError()

    return dni, date, cp


def _is_dni_letter_correct(dni):
    dni_num = int(dni[:-1])
    letter_num = int(dni_num/23)
    letter_num *= 23
    letter_num = dni_num-letter_num
    return _DNI_LETTERS[letter_num] == dni[-1]


if __name__ == '__main__':
    from log_helper import config_logging
    config_logging()
    res = answer(' '.join(sys.argv[1:]))
    print()
    print(res)
