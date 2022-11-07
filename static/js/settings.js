import { getDeckNamesAndIds } from "./main_anki_actions.js";
import { updateLearnerSettings } from './helpers.js';

async function setup() {
    const deckNamesAndIds = await getDeckNamesAndIds();
    // If we got here, then there's no exceptions and we can show settings
    document.getElementById('settings-container').classList.remove('hidden');

    const settings = JSON.parse(document.getElementById('settings').textContent);

    const languageSelector = document.getElementById('select-language');
    const current_language_code = settings['current_language_code'];
    // Fill languages selector
    settings['language_list'].forEach(language => {
        const opt = document.createElement('option');
        if (current_language_code === language['code']) {
            opt.selected = true;
        }
        opt.value = language['code'];
        opt.innerHTML = language['name'];
        languageSelector.appendChild(opt);
    });

    const deckSelector = document.getElementById('select-deck');

    // Fill deck selector
    for (const [key, value] of Object.entries(deckNamesAndIds)) {
        const opt = document.createElement('option');
        if (value === settings['deck_id']) {
            opt.selected = true;
        }
        opt.value = value;
        opt.innerHTML = key;
        deckSelector.appendChild(opt);
    }

    const showMessageOnCardAddition = document.getElementById('show-message-on-card-addition');
    showMessageOnCardAddition.checked = settings['show_message_on_card_addition'];

    document.getElementById('button-save').addEventListener('click', () => {
        const settings = {
            'language': languageSelector.value,
            'deck_id': deckSelector.value,
            'show_message_on_card_addition': showMessageOnCardAddition.checked,
        };
        updateLearnerSettings(settings, true);
    });
}

window.onload = setup;