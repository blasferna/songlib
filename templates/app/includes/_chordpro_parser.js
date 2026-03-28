/* Shared ChordPro client-side parser.
   Provides: parseChordProLine(line) and renderChordProHtml(text)
   Requires: escapeHtml(text) to be defined before inclusion.
*/
function parseChordProLine(line) {
    var segments = [];
    var regex = /\[([^\]]+)\]/g;
    var lastIndex = 0;
    var match;
    while ((match = regex.exec(line)) !== null) {
        if (match.index > lastIndex) {
            var beforeText = line.substring(lastIndex, match.index);
            if (segments.length > 0) {
                segments[segments.length - 1].text += beforeText;
            } else {
                segments.push({chord: '', text: beforeText});
            }
        }
        segments.push({chord: match[1], text: ''});
        lastIndex = regex.lastIndex;
    }
    if (lastIndex < line.length) {
        var remaining = line.substring(lastIndex);
        if (segments.length > 0) {
            segments[segments.length - 1].text += remaining;
        } else {
            segments.push({chord: '', text: remaining});
        }
    }
    if (segments.length === 0) {
        segments.push({chord: '', text: '\u00a0'});
    }
    return segments;
}

function renderChordProHtml(text) {
    if (!text.trim()) return '';
    var lines = text.split('\n');
    var html = '';
    for (var i = 0; i < lines.length; i++) {
        var segments = parseChordProLine(lines[i]);
        html += '<div class="chord-line-wrapper"><div class="chord-line-content">';
        for (var j = 0; j < segments.length; j++) {
            var s = segments[j];
            html += '<span class="chord-pair">';
            html += '<span class="chord-annotation">' + (s.chord ? escapeHtml(s.chord) : '') + '</span>';
            html += '<span class="chord-text">' + escapeHtml(s.text) + '</span>';
            html += '</span>';
        }
        html += '</div></div>';
    }
    return html;
}
