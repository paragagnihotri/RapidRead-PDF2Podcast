from crewai import Task

def create_tasks(agents: dict):
    """
    Create and return all CrewAI tasks
    
    Args:
        agents: Dictionary containing all agent instances
        
    Returns:
        Dictionary of task instances
    """
    
    pdf_cleaning_task = Task(
        agent=agents["pdf_cleaner"],
        description=(
            "Clean the raw PDF text by:\n"
            "1. Using the Text Cleaner tool to remove redundant headers, footers, and page numbers\n"
            "2. Eliminating excessive whitespace and irregular line breaks\n"
            "3. Preserving all meaningful content and structure\n\n"
            "Raw content:\n{raw_content}\n\n"
            "Return ONLY the cleaned text without any explanations."
        ),
        expected_output="Clean, well-formatted text with all original content preserved and PDF artifacts removed."
    )
    
    content_analysis_task = Task(
        agent=agents["content_analyzer"],
        description=(
            "Analyze the cleaned text and create a comprehensive outline of all topics and key points. "
            "Your analysis should include:\n"
            "1. Main topics and themes\n"
            "2. Subtopics and supporting concepts\n"
            "3. Important technical details, definitions, and explanations\n"
            "4. Examples, use cases, or scenarios mentioned\n"
            "5. Any warnings, best practices, or recommendations\n\n"
            "Organize this as a structured outline that will guide the conversation creation. "
            "Ensure EVERY important point from the document is captured.\n\n"
            "Use the cleaned text from the previous task."
        ),
        expected_output=(
            "A detailed, structured outline covering all main topics, subtopics, and key points from the document. "
            "This should serve as a complete roadmap for the conversation."
        ),
        context=[pdf_cleaning_task]
    )

    dialogue_building_task = Task(
        agent=agents["dialogue_builder"],
        description=(
            "Based on the content analysis, design the audio discussion structure between Adam and Eve. "
            "Create a dialogue flow plan that includes:\n"
            "1. Introduction where both speakers introduce the topic together with natural energy\n"
            "2. Logical progression through all topics from the analysis with smooth transitions\n"
            "3. Organic conversation flow that feels spontaneous and unscripted\n"
            "4. Back-and-forth discussion where both speakers contribute with varied vocal energy\n"
            "5. Exploration of examples and scenarios with natural reactions and responses\n"
            "6. Collaborative summary and conclusion with genuine warmth\n\n"
            "Design the conversation to sound natural when spoken aloud:\n"
            "- Varied sentence lengths and rhythms (mix of short, punchy and longer, flowing)\n"
            "- Natural verbal expressions of emotion (excitement, curiosity, agreement, thoughtfulness)\n"
            "- Spontaneous conversational moments (friendly interruptions, finishing thoughts, shared humor)\n"
            "- Realistic pacing with quick exchanges and thoughtful moments\n"
            "- Natural speech patterns that people actually use in conversation\n\n"
            "Both speakers are knowledgeable peers with distinct personalities who:\n"
            "- Express genuine interest and enthusiasm through their words\n"
            "- Show emotional engagement through natural speech\n"
            "- Have authentic verbal reactions to ideas\n"
            "- Build rapport through humor and shared understanding\n"
            "- Have equal participation with complementary conversational styles\n\n"
            "Design this as an audio-first discussion blueprint that will sound like a real, engaging conversation."
        ),
        expected_output=(
            "A detailed discussion blueprint outlining the flow, topic progression, interaction style, "
            "emotional beats, and natural conversational elements between two expressive speakers having "
            "a balanced, collaborative, and genuinely human audio conversation covering all topics."
        ),
        context=[content_analysis_task]
    )

    script_writing_task = Task(
        agent=agents["script_writer"],
        description=(
            "Write a complete, natural, expressive audio discussion between Adam and Eve following the designed structure. "
            "This script will be converted to audio, so every word must sound natural when spoken aloud.\n\n"
            "CONTENT REQUIREMENTS:\n"
            "1. Cover ALL topics identified in the content analysis thoroughly\n"
            "2. Feature both speakers as knowledgeable peers with distinct conversational styles\n"
            "3. Include balanced participation where both speakers contribute meaningfully\n"
            "4. Ensure accurate technical content while maintaining natural flow\n\n"
            "NATURAL SPEECH REQUIREMENTS (No visual directions - audio only):\n"
            "5. Use natural speech patterns and verbal expressions:\n"
            "   - Conversational fillers: 'you know', 'I mean', 'like', 'actually', 'right', 'so', 'well'\n"
            "   - Thinking aloud: 'let me think...', 'hmm...', 'how do I put this...'\n"
            "   - Natural pauses: 'So... yeah', 'And... well...', ellipses for trailing off\n"
            "   - Self-corrections: 'I mean, not exactly, but...', 'Well, more like...'\n"
            "   - Verbal emphasis: 'Really', 'Exactly', 'Absolutely', 'Totally'\n"
            "6. Show emotion and expression through words and speech:\n"
            "   - Laughter and humor: 'Ha!', 'Haha, that's great!', 'That's hilarious!'\n"
            "   - Excitement: 'Oh wow!', 'That's fascinating!', 'Oh man!', 'No way!'\n"
            "   - Agreement: 'Yes!', 'Exactly!', 'Right!', 'Totally!', 'For sure!'\n"
            "   - Curiosity: 'Really?', 'Wait, seriously?', 'Huh, interesting...'\n"
            "   - Thoughtfulness: 'You know what...', 'Here's the thing...', 'Actually...'\n"
            "7. Create natural conversational rhythm:\n"
            "   - Vary sentence length (short punchy reactions, longer explanations)\n"
            "   - Use fragments like real speech: 'But yeah.', 'So, basically.', 'I mean...'\n"
            "   - Include vocal sounds: 'Mmm', 'Ah', 'Oh', 'Uh-huh', 'Yeah yeah'\n"
            "   - Use em dashes (—) for interruptions or sudden thoughts\n"
            "   - Let speakers interrupt naturally when excited: 'Oh! Oh! And another thing—'\n"
            "8. Build authentic back-and-forth:\n"
            "   - Finishing each other's thoughts naturally\n"
            "   - Quick agreements: 'Right, right.', 'Mhmm, yeah.', 'Exactly.'\n"
            "   - Building on points: 'And on that note...', 'Speaking of which...'\n"
            "   - Friendly interruptions from enthusiasm (not rudeness)\n"
            "   - Shared moments: 'Haha, we're totally on the same page.'\n"
            "9. Make it sound unrehearsed:\n"
            "   - Occasional verbal stumbles that get corrected naturally\n"
            "   - Sentences that evolve as the speaker talks\n"
            "   - Side comments and tangents that circle back\n"
            "   - Moments where speakers think out loud before landing on their point\n\n"
            "DIALOGUE FORMAT (Clean, audio-ready):\n"
            "Adam: Natural dialogue that sounds real when spoken...\n\n"
            "Eve: Response with natural speech patterns and verbal expressions...\n\n"
            "EXAMPLES OF NATURAL AUDIO DIALOGUE:\n"
            "Adam: Oh wow, that's such a great point! And you know what else I've been thinking about?\n\n"
            "Eve: Mm, what's that?\n\n"
            "Adam: So, like, when you really look at it... I mean, the whole thing kind of connects, right?\n\n"
            "Eve: Oh absolutely! Actually — and this is interesting — I was just reading about this and—\n\n"
            "Adam: Right! Yes! That's exactly where I was going with this. It's like...\n\n"
            "Eve: Haha, we're totally on the same wavelength here. But yeah, so basically...\n\n"
            "CRITICAL: NO stage directions, NO bracketed instructions, NO visual cues whatsoever. "
            "Everything must be conveyed through the actual spoken words. The script should read like a "
            "transcript of a real conversation - words only, pure dialogue that sounds natural when performed."
        ),
        expected_output=(
            "A complete, natural audio discussion script with:\n"
            "- Adam and Eve speaker labels only\n"
            "- Pure dialogue with NO stage directions or visual cues\n"
            "- Natural speech patterns, fillers, pauses, and verbal expressions built into the dialogue itself\n"
            "- Vocal expressions (laughter, excitement, agreement) written as actual words\n"
            "- Balanced, expressive participation from both speakers\n"
            "- Rhythm and pacing that sounds natural when read aloud\n"
            "- Ready-to-record script that will sound like a genuine, spontaneous audio conversation"
        ),
        context=[content_analysis_task, dialogue_building_task]
    )

    quality_assurance_task = Task(
        agent=agents["quality_assurance"],
        description=(
            "Review the conversation script and ensure:\n"
            "1. All topics from the content analysis are covered\n"
            "2. The dialogue sounds natural and flows well\n"
            "3. Proper script formatting is maintained\n"
            "4. No important information is missing\n"
            "5. The conversation is engaging and easy to follow\n\n"
            "If any topics are missing or dialogue needs improvement, note what should be added. "
            "Provide the final, polished script ready to be saved.\n\n"
            "Format the output as a clean script with clear speaker labels."
        ),
        expected_output=(
            "A finalized, well-formatted conversation script that is complete, natural-sounding, "
            "and covers all important points from the original PDF. Ready to be saved to a file."
        ),
        context=[content_analysis_task, script_writing_task]
    )
    
    return {
        "pdf_cleaning": pdf_cleaning_task,
        "content_analysis": content_analysis_task,
        "dialogue_building": dialogue_building_task,
        "script_writing": script_writing_task,
        "quality_assurance": quality_assurance_task
    }