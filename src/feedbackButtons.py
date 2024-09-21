from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class FeedbackButtons:
    @staticmethod
    def create_feedback_buttons():
        # Create the inline keyboard with thumbs up and thumbs down buttons
        markup = InlineKeyboardMarkup(row_width=2)
        thumbs_up = InlineKeyboardButton("👍", callback_data="like")
        thumbs_down = InlineKeyboardButton("👎", callback_data="dislike")
        markup.add(thumbs_up, thumbs_down)
        return markup
