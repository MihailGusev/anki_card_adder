import { enableControlWhenTextIsNotBlank, postJson } from "./helpers.js";
import { showInfo, showError } from './main_interface_manager.js';

const feedbackArea = document.getElementById('feedback-area');
const sendButton = document.getElementById('send-button');

enableControlWhenTextIsNotBlank(sendButton, feedbackArea);

sendButton.addEventListener('click', async () => {
    try {
        await postJson('feedback/', { 'feedback': feedbackArea.value });
        feedbackArea.value = '';
        showInfo("Thank you!", 2);
    }
    catch {
        showError('Unable to send feedback to the server');
    }
});