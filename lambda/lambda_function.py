# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#Constants
N8N_WEBHOOK_URL = "https://primary-production-84ee1.up.railway.app/webhook"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Student Mode. What would you like to do?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class SummarizeEmailsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("summarize_emails")(handler_input)
    
    def handle(self, handler_input):
        response = requests.get(N8N_WEBHOOK_URL + "/summarizeEmails")
        
        data = response.json()
        
        summary = data.get("output", "")
        if response.status_code == 200:
            if len(summary) == 0:
                speak_output = "You have no new emails!"
            else:
                speak_output = "Here is a summary of your most recent emails: " + data.get("output", "")
        else:
            speak_output = "There was an error connecting with the server."
                
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )

class CheckAssignmentsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("check_canvas_assignments")(handler_input)
    
    def handle(self, handler_input):
        response = requests.get("https://canvas-alexa-493d4ce1b701.herokuapp.com/canvas/assignments")
        
        if response.status_code == 200:
            #TODO: update to return real response
            speak_output = "You have no upcoming assignments. Well done!"
        else:
            speak_output = "There was an error conencting with the server."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class SendEmailIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("draft_email")(handler_input)
    
    def handle(self, handler_input):
        description = ask_utils.get_slot_value(handler_input=handler_input, slot_name="content")
        response = requests.post(N8N_WEBHOOK_URL + "/writeDraft", json={"description": description})
        
        if response.status_code == 200:
            speak_output = "Email created!"
        else:
            speak_output = "Failed to create email."
                
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )

class DraftResponseIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("draft_reply")(handler_input)
    
    def handle(self, handler_input):
        name = ask_utils.get_slot_value(handler_input=handler_input, slot_name="name")
        description  = ask_utils.get_slot_value(handler_input=handler_input, slot_name="reply")
        response = requests.post(N8N_WEBHOOK_URL + "/draftResponse", json={"from":name, "reply":description})
        
        if response.status_code == 200:
            speak_output = "Reply created!"
        else:
            speak_ouput = "Failed to create draft."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class CanvasGradesIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("check_canvas_grades")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Extract the value of the slot named "class"
        class_name = ask_utils.get_slot_value(handler_input=handler_input, slot_name="class")

        if class_name:
            # This is where you'd call your Canvas API or Semantic Matching
            clean_name = class_name.replace(" ", "%20")
            response = requests.get("https://canvas-alexa-493d4ce1b701.herokuapp.com/canvas/grades/" + clean_name)
            
            data = response.json()
            
            grade = data.get("grade", "not found")
            
            speak_output = "Your grade is a " + str(grade) + " percent"
            
        else:
            speak_output = "I'm sorry, I didn't catch the name of the class."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CanvasGradesIntentHandler())
sb.add_request_handler(SendEmailIntentHandler())
sb.add_request_handler(SummarizeEmailsIntentHandler())
sb.add_request_handler(CheckAssignmentsIntentHandler())
sb.add_request_handler(DraftResponseIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()