from app.validation.abstract_validator import AbstractValidator
from app.validation.validation_result import ValidationResult
from gettext import gettext as _


class RequiredCheck(AbstractValidator):

    """
    Validate that a field is required
    :param user_answer: The answer the user provided for the response
    :return: ValidationResult(): An object containing the result of the validation
    """

    def validate(self, user_answer):

        validation_result = ValidationResult()

        if user_answer and not str(user_answer).isspace():
            validation_result.is_valid = True
        else:
            validation_result.is_valid = False
            validation_result.errors.append(_('This is a required field'))
        return validation_result
