from django.core.validators import RegexValidator

# Validators for field 'username' in Usermodel!
REGEX_SIGNS = RegexValidator(r'^[\w.@+-]+\Z', 'Поддерживаемые знаки.')
# Validators for field 'color' in Tag!
REGEX_COLOR = RegexValidator(r'^#[0-9A-F]{6}$', 'Поддерживаемые знаки.')
# Validators for field 'slug' in Tag!
REGEX_SLUG = RegexValidator(r'^[-a-zA-Z0-9_]+$', 'Поддерживаемые знаки.')
# Validators for field 'amount' in RecipeIngredient!
REGEX_AMOUNT = RegexValidator(r'^[1-9][0-9]*$', 'Укажите значение кол-ва '
                              'добавляемого ингридиента больше 0.')
# Constants for models!
NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
TEXT_MAX_LENGTH = 200
# Default pagination size!
DEFAULT_PAGES_LIMIT = 6
