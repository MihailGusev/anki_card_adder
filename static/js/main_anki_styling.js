// Markup and styles for cards
// Words in double curly braces are note fields
// Reference: https://docs.ankiweb.net/templates/fields.html

/**
 * Template for the front side of the card
 */
export const frontSide = `<div class=main>
{{TranslationString}}
</div>`;

/**
 * Template for the back side of the card (only for English words because of the dictionary links)
 */
export const backSide = `{{FrontSide}}

<hr>

<div class=main>
  {{Word}} - {{Transcription}} - {{Sound}}
</div>

{{Context}}
<br>
<br>

{{TranslationTable}}
<br>

{{DefinitionTable}}
<br/>

<a href="https://translate.google.com/?sl=en&tl={{text:TranslateTo}}&text={{text:Word}}">Google</a>
<a href="https://www.collinsdictionary.com/dictionary/english/{{text:Word}}">Collins</a>
<a href="https://dictionary.cambridge.org/dictionary/english/{{text:Word}}">Cambridge</a>
<a href="https://www.oxfordlearnersdictionaries.com/definition/english/{{text:Word}}">Oxford</a>`;

/**
 * Styles for cards
 */
export const css = `.card {
  font-family: georgia;
  font-size: 20px;
}

.main {
  text-align: center;
  font-size: 30px;
}

table {
  border-collapse: collapse;
  width: 100%;
}

table td, table th {
  border: 1px solid #ccc;
  padding: 5px;
}

table tr:nth-child(even){
  background-color: #ddd;
}

table th {
  padding-top: 7px;
  padding-bottom: 7px;
  text-align: left;
  background-color: #04aa6d;
  color: white;
}

.card.nightMode {
  color: #f8e8bf;
}

.nightMode table tr:nth-child(even){
  background-color: #444;
}`;