"""Plain-language interpretations ("what this means for you").

Planet-in-house results are paraphrased from classical Jyotish foundations:
Brihat Parashara Hora Shastra (Bhava-phala chapters), Phaladeepika ch. 8 and Saravali.
Each entry = (what tends to happen in everyday life, what to be mindful of).
Dignity, functional role and Shadbala decide how strongly the positive or demanding side manifests.
"""
from __future__ import annotations

# (life effect: 3-4 descriptive sentences, caution: 2-3 constructive guidance sentences)
PLANET_IN_HOUSE: dict[str, dict[int, tuple[str, str]]] = {
    "Sun": {
        1: (
            "You carry natural dignity, presence and self-respect. People notice when you walk into a room, and you naturally take initiative rather than waiting for instructions. You hold firm principles, value honour and honesty, and feel best when you have autonomy in your work.",
            "Watch a tendency toward pride, impatience or appearing unapproachable to those who need gentleness. Physical vitality is strong, but take care of your heart, eyesight, and avoid dehydration or excess heat during intense work.",
        ),
        2: (
            "Your speech carries authority and confidence, and people tend to take your word seriously. You are motivated to build family status and earn through honourable channels, government links, or leadership roles. You take pride in providing for those close to you.",
            "Be mindful of blunt or sharp speech during disagreements, as words spoken in pride can wound family harmony. Keep financial planning steady and avoid speculative or image-driven spending.",
        ),
        3: (
            "You possess courage, vigour and strong communication skills. You are resourceful, enjoy taking the lead in group efforts, and do well in writing, media, technology, or independent ventures where courage pays off. Your willpower helps you push through obstacles that deter others.",
            "Watch for unnecessary competition with siblings, cousins or neighbours. Channel your drive into creative and physical outlets rather than verbal debates or hasty risks.",
        ),
        4: (
            "You desire a home that feels dignified, stable and reputable. You often gain respect or property through family lineage or public connections, and you take pride in establishing your own ground. You have a deep inner sense of personal code.",
            "Domestic peace may sometimes feel elusive because the Sun's fiery nature can create formal or demanding relationships at home. Take time to relax your standards with loved ones and express warmth freely.",
        ),
        5: (
            "Your mind is creative, sharp and drawn to intellectual leadership. You enjoy learning, express yourself with flair, and have good instincts for administration, mentorship, and creative projects. People respect your judgment and advice.",
            "Avoid letting pride influence your romantic life or relationships with children. When investing, rely on thorough research and disciplined methods rather than speculative pride.",
        ),
        6: (
            "This is a powerful placement for resilience, hard work and overcoming hurdles. You are not easily discouraged by rivals, legal challenges or competitive environments, and you do well in service, healthcare, law, or problem-solving roles.",
            "Do not let work consume your daily life or create chronic stress. Pay attention to digestion, acidity and blood pressure, and make time for restorative rest between demanding periods.",
        ),
        7: (
            "You are drawn to partners who have strong willpower, distinction or independent status. Partnerships, whether in business or personal life, are central to your growth and teach you how to balance self-assertion with compromise.",
            "Ego clashes are the primary hurdle in close relationships when two strong personalities collide. Cultivate active listening, share the spotlight generously, and avoid turning domestic decisions into matters of prestige.",
        ),
        8: (
            "You possess deep investigative ability, psychological insight and courage in crisis. You are drawn to understand the hidden mechanics of life, whether through research, finance, psychology, or spiritual inquiry. Significant turning points often renew your strength.",
            "Guarding against secrecy, sudden disputes over shared resources, or neglect of personal vitality. Protect eye and cardiac health, and maintain open communication with mentors and elders.",
        ),
        9: (
            "You have high ideals, a philosophical outlook and deep respect for truth, mentors and heritage. Higher learning, teaching, law, and long journeys expand your horizon, and you often receive goodwill from teachers and institutions.",
            "Be careful not to become dogmatic or dismissive of viewpoints that differ from your own. Differences of opinion with father figures or teachers are best handled with patience and humility.",
        ),
        10: (
            "This is one of the most celebrated placements for public achievement and professional status. You naturally take charge, earn recognition from superiors, and thrive in administration, government, management, or visible executive roles. Your reputation matters greatly to you.",
            "Guard against letting professional ambition crowd out your personal and family life. Ensure that confidence does not drift into autocracy, and remain supportive of team members who work under you.",
        ),
        11: (
            "You build alliances with influential people and work purposefully toward your long-term goals. Your ambitions tend to materialize through steady effort, and you enjoy gathering a supportive network of colleagues and mentors.",
            "Ensure that friendships are based on genuine mutual respect rather than purely practical or status considerations. Stay disciplined with windfalls and avoid risky speculative group ventures.",
        ),
        12: (
            "You have a quiet, reflective inner life and a natural curiosity about foreign cultures, spiritual study, or behind-the-scenes work. You find strength in solitude and often do meaningful work away from the public gaze, such as in research or institutions.",
            "Recognition for your efforts may feel delayed or unacknowledged at times. Guard against depleted energy, ensure adequate sleep, and keep financial accounts organized to manage unexpected expenses.",
        ),
    },
    "Moon": {
        1: (
            "You are intuitive, responsive, and connect naturally with the feelings of those around you. People find you approachable and gentle, and you adapt easily to shifting environments. Your imagination and memory are rich, giving you artistic and social warmth.",
            "Because your emotions are so close to the surface, moods can fluctuate quickly and cloud objective decision-making. Build grounding daily routines, spend time near water or in nature, and avoid taking on everyone else's emotional burdens.",
        ),
        2: (
            "You express yourself with warmth and care, making family and domestic nourishment central to your life. You have a good instinct for accumulating comforts, saving for the future, and creating a hospitable environment for loved ones.",
            "Financial income and expenditure can follow emotional cycles, rising with confidence and dipping during stress. Watch a tendency toward comfort-eating or impulsive shopping when emotionally unsettled.",
        ),
        3: (
            "You possess an agile, curious mind with a talent for storytelling, writing, and creative communication. You enjoy short trips, community activities, and maintaining close ties with siblings and friends. You learn quickly and bring freshness to whatever you share.",
            "Restlessness can cause you to juggle too many interests at once and leave projects unfinished. Focus on seeing one creative goal through before starting another, and calm your nervous system with quiet breaks.",
        ),
        4: (
            "This is a deeply comforting placement that gives a strong attachment to home, heritage, and peace of mind. You find rejuvenation in your private sanctuary, enjoy hospitality, and share a meaningful bond with your mother or maternal lineage.",
            "Over-attachment to familiar surroundings can make necessary changes or relocations feel painful. Learn to carry your inner sanctuary with you, and avoid dwelling on past grievances or family nostalgia.",
        ),
        5: (
            "Your mind is imaginative, poetic, and rich in creative instincts. You have natural empathy for children, enjoy intellectual and artistic hobbies, and approach life with a playful, romantic heart. Your intuitive hunches are often surprisingly accurate.",
            "Emotions can easily overpower logic in matters of the heart or financial investments. Anchor your enthusiasm with objective counsel, and avoid letting romantic daydreaming distract from practical responsibilities.",
        ),
        6: (
            "You have a genuine heart for service, healing, and helping others through difficulties. You excel in healthcare, hospitality, social support, or detailed administrative roles where empathy and attention to daily needs are required.",
            "You tend to absorb workplace stress and worry excessively about everyday problems. Guard your digestive health and fluid balance, and establish clear boundaries so you do not carry other people's anxieties home.",
        ),
        7: (
            "You desire emotional intimacy and mutual nurturing in your partnerships. You relate easily to the public, do well in customer-facing or collaborative work, and flourish when you share life with a caring, emotionally supportive partner.",
            "Emotional expectations of your partner can be high, leading to moodiness if they seem distant. Keep open, gentle dialogue going, and develop personal interests so your partner is not your only source of emotional balance.",
        ),
        8: (
            "You have deep emotional radar, psychological perceptiveness, and an interest in the mysteries of the mind. You can sense unspoken dynamics in any room, and you have the strength to heal from profound emotional shifts and personal transformations.",
            "Emotional anxiety, fear of abandonment, or mood swings can trouble your peace if unaddressed. Regular meditation, trusted confidants, and consistent sleep habits help keep your inner waters calm and steady.",
        ),
        9: (
            "You possess an open, idealistic mind that finds joy in travel, philosophy, spirituality, and higher learning. You have natural faith in life, appreciate diverse cultures, and enjoy exploring traditions that nurture the soul.",
            "Your philosophical beliefs may fluctuate depending on your emotional state. Anchor your ideals in steady daily practice rather than chasing novel experiences whenever routine feels dull.",
        ),
        10: (
            "Your professional life benefits from public goodwill, popular appeal, and an ability to sense what people need. You do well in public relations, education, healthcare, human resources, or hospitality where a human touch makes the difference.",
            "Your professional reputation can be sensitive to public mood, and career changes may follow shifting emotional phases. Keep long-term goals in sight, and avoid changing roles impulsively during temporary periods of dissatisfaction.",
        ),
        11: (
            "You are warmly supported by friends, social groups, and community networks, often receiving guidance from women. You take pleasure in shared humanitarian or creative goals, and your income tends to flow well through collaborative efforts.",
            "Financial gains and friendships can fluctuate if boundaries are blurred. Cultivate a dependable inner circle, and ensure your long-term aspirations are grounded in realistic planning.",
        ),
        12: (
            "You possess a sensitive, reflective soul with a rich inner dream life and a strong affinity for solitude, meditation, and spiritual retreat. You may feel a pull toward distant lands or finding peace away from the noise of modern life.",
            "You can easily feel drained by crowded environments or emotional overload. Guard your sleep, protect yourself from escapist habits, and keep finances orderly so that generosity does not leave you vulnerable.",
        ),
    },
    "Mars": {
        1: (
            "You are energetic, decisive, and courageous, with a natural drive to take on challenges head-on. You speak directly, act without hesitation, and inspire others through your physical stamina and competitive spirit.",
            "Impatience, a quick temper, or rushing into physical activity can lead to minor accidents or friction with others. Channel your abundant vitality into regular physical training, and count to ten before responding in heated moments.",
        ),
        2: (
            "You are fiercely determined to build financial security and provide for your household through hard work. You have strong willpower regarding family resources, and you do well in technical, engineering, culinary, or property-related enterprises.",
            "Watch for sharp or blunt speech that can unintentionally wound family members. Avoid aggressive or impulsive financial risks, and maintain balanced, unhurried eating habits.",
        ),
        3: (
            "Your courage, initiative, and manual dexterity are exceptional. You tackle difficult projects with enthusiasm, excel in competitive fields, sales, engineering, sports, or hands-on skills, and stand up readily for what you believe.",
            "Disagreements or rivalry with siblings, colleagues, or neighbours can emerge if you push too hard. Direct your competitive fire toward self-improvement rather than trying to prove a point to others.",
        ),
        4: (
            "You have strong drive to acquire land, real estate, vehicles, or construct a resilient home environment. You protect your family fiercely and have the stamina to manage demanding domestic and property responsibilities.",
            "The home environment can easily become tense or argumentative if your inner restlessness is not addressed. Practice patience with household members, and create quiet physical spaces to decompress.",
        ),
        5: (
            "Your intellect is sharp, strategic, and quick to grasp complex problems. You have a passion for competitive fields, technical studies, sports, or creative projects that require decisive action and problem-solving.",
            "In romance, you may be prone to sudden passions followed by impatience. When investing, avoid high-risk speculation driven by the desire for quick wins, and practice patience with children's individual pace.",
        ),
        6: (
            "This is an outstanding placement for overcoming opposition, tackling complex problems, and outworking rivals. You possess excellent stamina, strong immunity, and thrive in law, medicine, service, or high-pressure problem-solving environments.",
            "Do not let your competitive drive turn daily life into a battlefield. Avoid over-exhaustion, manage inflammation or fever promptly, and resolve disputes through calm negotiation whenever possible.",
        ),
        7: (
            "You bring intense passion, energy, and drive into partnerships. You are attracted to dynamic, proactive partners and can build successful enterprises together when goals are aligned.",
            "This placement contributes to Manglik dosha; arguments, jealousy, or a battle of wills can test the relationship. Clear communication, mutual respect for autonomy, and avoiding haste in marriage decisions are essential.",
        ),
        8: (
            "You have tremendous resilience and courage during life crises, emergency situations, or deep research. You are not afraid to face difficult realities and can excel in surgery, investigation, engineering, or managing joint finances.",
            "Take care while driving, handling tools, or engaging in extreme sports to avoid injuries. Maintain transparent financial dealings regarding inheritance or shared assets, and allow yourself time to process emotional tension.",
        ),
        9: (
            "You stand up courageously for your principles, justice, and beliefs. You are willing to blaze your own trail in higher studies, travel to challenging destinations, and defend ethical causes with genuine passion.",
            "Avoid dogmatic arguments or clashes of ego with father figures, mentors, or traditional institutions. Temper your zeal with wisdom, and remember that persuasion is more effective than confrontation.",
        ),
        10: (
            "This is one of Mars's finest placements (Kuladeepaka), giving extraordinary drive, professional courage, and leadership. You rise through action, manage crises calmly, and do exceptionally well in executive roles, defence, police, engineering, or entrepreneurship.",
            "Demanding standards can make you a harsh taskmaster with subordinates or colleagues. Cultivate warmth alongside authority, and avoid burning yourself out in pursuit of rapid career milestones.",
        ),
        11: (
            "You pursue your goals with relentless focus and tend to achieve substantial material gains through your own efforts. You enjoy ambitious networks, work well in goal-driven teams, and can profit through land, property, or technical ventures.",
            "Friendships can become strained if competitive rivalry enters the relationship. Ensure that collaborative ventures have clearly documented agreements to prevent disputes over profits.",
        ),
        12: (
            "You direct considerable energy toward behind-the-scenes work, international ventures, or independent projects. You can be quietly fearless when working away from the public gaze, such as in research, foreign projects, or charitable service.",
            "Energy can leak through interrupted sleep, hidden frustrations, or unplanned expenses. Maintain a calm bedtime routine, practice relaxation techniques, and avoid impulsive financial commitments abroad.",
        ),
    },
    "Mercury": {
        1: (
            "You have a youthful, curious, and witty nature with sharp analytical ability. You express yourself fluently, pick up new skills with ease, and adapt smoothly to diverse social and professional environments. People appreciate your intelligence and light-hearted humour.",
            "Your mind can easily become overactive, leading to nervous tension, restlessness, or difficulty switching off at night. Ground yourself through physical activity, take breaks from screens, and finish core priorities before starting new projects.",
        ),
        2: (
            "You are articulate, persuasive, and possess a talent for trade, numbers, writing, or education. Your voice is pleasant and intelligent, and you earn through communication, commerce, consulting, or analytical expertise. You enjoy intellectual family discussions.",
            "Be mindful not to let cleverness turn into verbal sarcasm or over-calculating in personal relationships. Keep financial records transparent, and avoid getting caught in over-complex financial schemes.",
        ),
        3: (
            "Your communicative and literary skills are exceptional. You excel in writing, digital media, marketing, IT, teaching, or commercial networking. You learn rapidly, write persuasively, and enjoy vibrant connections with siblings, peers, and your local community.",
            "Having so many interests can scatter your energy and lead to superficial focus. Train yourself to specialize in a few valuable skills, and manage your nervous energy with quiet reflection.",
        ),
        4: (
            "You value an intellectually stimulating home with books, conversation, and modern communication. You do well in education, research, real estate documentation, or working from home, and you share an intellectual bond with maternal figures.",
            "A restless mind can make it difficult to feel settled or completely at ease in your domestic life. Keep your living space organized, create quiet zones free from work devices, and allow time for mental peace.",
        ),
        5: (
            "You possess a sharp, inventive intellect with a knack for analysis, strategy, coding, or creative writing. You enjoy intellectual puzzles, excel in academic exams, and communicate with charm and playfulness in romance.",
            "Over-analysing emotions can cause indecision or hesitation in love and personal commitments. When investing, rely on structured research rather than quick speculative trading that drains your mental focus.",
        ),
        6: (
            "You are exceptionally skilled at problem-solving, detailed analysis, accounting, and organizing complex systems. You thrive in legal, medical, administrative, or technical roles where accuracy and discernment are paramount.",
            "Excessive attention to flaws can lead to chronic worry, perfectionism, or stress-related digestive and nervous issues. Learn to accept 'good enough' when perfection is unnecessary, and maintain regular meal schedules.",
        ),
        7: (
            "You seek an intelligent, witty, and articulate partner with whom you can share lively ideas and mutual companionship. You excel in commercial negotiation, public relations, consulting, and collaborative business partnerships.",
            "Treating relationships purely as practical contracts can leave emotional needs unmet. Balance logic with heart-to-heart warmth, and avoid over-debating small household disagreements.",
        ),
        8: (
            "You have a natural investigative mind, well suited for deep research, data analysis, forensic accounting, tax, or esoteric study. You enjoy unraveling secrets, solving mysteries, and understanding the subtext beneath spoken words.",
            "Mental strain or anxiety can trouble you if you dwell on worst-case scenarios. Protect your nervous system with restorative sleep, and avoid secrecy in financial or legal matters.",
        ),
        9: (
            "You have a lifelong love of learning, philosophical inquiry, writing, and cross-cultural study. You do well in teaching, publishing, law, or research, and you enjoy travel that broadens your knowledge and introduces you to fresh perspectives.",
            "Curiosity can sometimes lead to sampling many philosophical paths without committing deeply to any. Cultivate depth in your chosen field of study, and maintain respect for the wisdom of seasoned mentors.",
        ),
        10: (
            "You build a successful career through communication, commerce, technology, management, or advisory services. You are versatile, handle multiple projects skillfully, and earn a reputation for competence, quick learning, and practical intelligence.",
            "Spreading yourself across too many professional roles can delay reaching senior leadership. Choose a clear central focus, delegate routine tasks, and ensure that substance always matches your articulate presentation.",
        ),
        11: (
            "You build a wide, intellectually engaging network of friends, colleagues, and associates. You earn well through commerce, group ventures, technology, or advisory work, and your adaptable nature helps you seize opportunities quickly.",
            "Some social connections may remain superficial if you prioritize quantity over depth. Nurture a few deeply loyal friendships, and stay disciplined with financial planning when earnings fluctuate.",
        ),
        12: (
            "You have an imaginative, introspective mind drawn to foreign languages, creative writing, research, or spiritual literature. You do your best creative and analytical thinking in quiet solitude, away from everyday distractions.",
            "A tendency to worry late at night can interfere with restful sleep. Establish clear boundaries around evening work, practice calming meditation, and keep your financial accounts well organized.",
        ),
    },
    "Jupiter": {
        1: (
            "This is one of the most benevolent placements in Vedic astrology, bestowing wisdom, optimism, and moral character. You carry natural grace, inspire trust in others, and enjoy broad protection for your vitality, reputation, and life direction.",
            "Watch a tendency toward over-optimism, weight gain, or assuming that good fortune will always handle the details. Ground your noble intentions in practical daily discipline and healthy physical routines.",
        ),
        2: (
            "Your words carry truth, warmth, and ethical weight, earning you respect in your family and community. You have excellent instincts for building steady wealth, supporting loved ones, and creating a cultured, harmonious household.",
            "Generosity can sometimes lead to overspending or lending money without clear terms. Maintain structured budgets, and avoid taking on financial responsibilities that belong to others.",
        ),
        3: (
            "You approach life with enthusiasm, optimism, and an encouraging attitude toward siblings and colleagues. You do well in writing, teaching, publishing, counselling, or community leadership, where your uplifting vision motivates others.",
            "You may sometimes lack the competitive aggression needed in cut-throat environments. Cultivate firmness alongside benevolence, and ensure that big promises are matched by steady execution.",
        ),
        4: (
            "You enjoy deep inner contentment, a supportive home, and blessings through your mother, education, and real estate. Your home is a place of learning and warmth, and you often acquire spacious property or vehicles that bring lasting comfort.",
            "Excessive comfort can sometimes dampen your professional ambition or lead to complacency. Stay engaged with meaningful life goals, and share your domestic blessings through hospitality.",
        ),
        5: (
            "This is a brilliant placement for intellect, wisdom, higher counsel, and creative expression. You have natural pedagogical ability, make sound ethical decisions, and experience deep joy through children, mentorship, or philosophical study.",
            "Classically, Jupiter here can occasionally bring minor delays in progeny or an over-idealistic view of romantic partners. Balance idealism with realistic expectations, and continue nurturing your intellectual gifts.",
        ),
        6: (
            "You have the wisdom to resolve disputes peacefully, turn adversaries into allies, and handle life's challenges with grace. You excel in service, medicine, law, counselling, or charitable work where your guidance relieves others' suffering.",
            "Watch dietary habits to protect your liver, metabolic health, and weight. Avoid signing surety bonds or taking on debts for friends without thorough evaluation.",
        ),
        7: (
            "You are blessed with a noble, wise, and supportive partner who brings growth and respect into your life. You do well in professional consulting, legal partnerships, and collaborative ventures built on mutual trust and shared values.",
            "Holding your partner to unrealistically high moral or intellectual standards can create subtle distance. Value their everyday humanity, and ensure that major life decisions are shared equally.",
        ),
        8: (
            "You possess spiritual depth, longevity, and a gift for research, metaphysics, or handling joint resources. You navigate life's major transitions with philosophical calm and can benefit through inheritance, insurance, or partner's fortunes.",
            "Gains through joint resources may involve delays or legal technicalities. Protect liver and digestive wellness through moderate diet, and use your psychological insight to heal rather than detach.",
        ),
        9: (
            "This is Jupiter's natural home, indicating extraordinary spiritual fortune, excellent mentors, and a lifelong thirst for truth. You earn respect through higher education, philosophy, law, or ethical leadership, and long journeys enrich your outlook.",
            "Guard against self-righteousness or preaching to those who are on a different stage of their journey. Let your conduct speak louder than your sermons, and remain a humble student of life.",
        ),
        10: (
            "You rise steadily to positions of authority, respect, and ethical leadership in your career. You excel in education, law, finance, government, or advisory roles, earning a reputation for integrity, fairness, and wise stewardship.",
            "Professional rise is usually steady rather than meteoric, requiring patience with early hurdles. Avoid compromising your ethical standards for short-term gain, as your long-term reputation is your greatest asset.",
        ),
        11: (
            "This placement brings abundant gains, influential mentors, and the realization of major life aspirations. You attract generous, wise friends, do well in large social or charitable organizations, and enjoy multiple streams of steady prosperity.",
            "Be discerning with acquaintances who seek your counsel or financial backing. Ensure that your resources are channelled into sustainable ventures rather than speculative group projects.",
        ),
        12: (
            "You have a profound spiritual inclination, a generous heart for charity, and a natural detachment from material greed. You find peace in meditation, pilgrimage, or quiet humanitarian work, and you may live or travel abroad with lasting benefit.",
            "Generosity and charitable spending can strain personal finances if not tracked carefully. Balance spiritual and philanthropic urges with practical financial reserves for your own security.",
        ),
    },
    "Venus": {
        1: (
            "You possess charm, graceful manners, and an innate sense of beauty, style, and harmony. People are naturally drawn to your pleasant disposition, and you excel in the arts, design, diplomacy, and interpersonal connections.",
            "Watch a tendency toward vanity, over-indulgence in pleasures, or avoiding necessary conflicts to keep a superficial peace. Develop internal discipline alongside your natural aesthetic gifts.",
        ),
        2: (
            "You speak with sweetness and melody, and you have an eye for luxury, fine food, and elegant possessions. You build wealth steadily through artistic, culinary, financial, or luxury-related ventures, and you bring harmony to family life.",
            "Expenditure on luxury, beauty, or entertaining can easily outpace savings if unmonitored. Maintain a firm financial plan, and avoid using shopping as an emotional pick-me-up.",
        ),
        3: (
            "You express yourself with artistic flair, poetic charm, and social warmth. You do well in media, design, music, performing arts, or literature, and you share affectionate, mutually supportive bonds with siblings and peers.",
            "You may shy away from tasks that feel tedious or physically demanding. Pair your creative inspiration with consistent follow-through, and stay focused when projects require patience.",
        ),
        4: (
            "You create a beautiful, welcoming, and artistic home filled with comfort, elegance, and warmth. You take pleasure in interior design, vehicles, and hosting loved ones, and you enjoy a loving relationship with maternal figures.",
            "Attachment to luxury and domestic ease can sometimes make you complacent or reluctant to embrace necessary life changes. Keep your creative passions alive outside the home.",
        ),
        5: (
            "You have a romantic, poetic heart with outstanding creative, theatrical, or artistic talents. You find immense joy in cultural pursuits, romance, and entertainment, and you share an affectionate, playful relationship with children.",
            "Romantic daydreams can cloud practical judgment in love or cause you to overlook important incompatibilities. When investing, avoid emotional or aesthetic impulses and stick to proven fundamentals.",
        ),
        6: (
            "You bring kindness, grace, and an eye for harmony into your daily work environment. You can do well in beauty, wellness, healthcare, interior styling, or service roles where making others comfortable is appreciated.",
            "Classically, Venus is in a sensitive position here; relationship friction, digestive imbalances, or health issues from over-indulgence can arise. Maintain clean daily habits and establish clear relationship boundaries.",
        ),
        7: (
            "This is a classical blessing for marriage, partnerships, and public dealings. You attract an attractive, loving, and cultured partner, and your shared life is characterized by affection, mutual support, and social grace.",
            "High romantic ideals can lead to disappointment if your partner does not constantly match your fantasy. Cherish the quiet, everyday moments of companionship, and resolve differences with gentle candour.",
        ),
        8: (
            "You experience deep, transformative partnerships and can gain financial benefits through marriage, inheritance, or joint investments. You have an appreciation for hidden aesthetics, psychology, and esoteric arts.",
            "Guarding against secrecy or complications in romantic and financial relationships. Prioritize reproductive and renal health, and ensure that financial agreements with partners are transparent and clear.",
        ),
        9: (
            "You possess a refined philosophical outlook, a love of sacred art and architecture, and fortune through travel. Your higher learning often involves arts, humanities, culture, or diplomacy, and you attract benevolent mentors.",
            "Pleasure-seeking or aesthetic comforts can sometimes distract you from deeper ethical discipline. Combine your appreciation for beauty with practical wisdom and authentic spiritual study.",
        ),
        10: (
            "Your professional life thrives in fields connected to arts, media, entertainment, fashion, luxury, hospitality, or diplomacy. You present yourself with elegance, work harmoniously with colleagues, and earn public admiration for your creative taste.",
            "Ensure that professional polish is matched by solid technical competence and reliability. Avoid relying solely on charm to advance, and remain grounded when public praise comes your way.",
        ),
        11: (
            "You enjoy abundant social popularity, warm friendships (often with creative women), and consistent financial gains. Your aspirations for comfort, creative fulfilment, and financial ease tend to be realized through cooperative ventures.",
            "Socializing and maintaining an active lifestyle can lead to high expenditures. Cultivate genuine friendships rather than surrounding yourself with fair-weather companions who share only your leisure time.",
        ),
        12: (
            "You have an intimate appreciation for private comforts, romantic devotion, and creative reflection in solitude. Classically, Venus here gives deep sleep, enjoyment of foreign travel, and quiet generosity toward spiritual or artistic causes.",
            "Spending on luxuries, retreats, or private indulgences can quietly erode your financial reserves. Keep track of discretionary expenses, and ensure that romantic decisions are made with eyes wide open.",
        ),
    },
    "Saturn": {
        1: (
            "You are serious, disciplined, and mature beyond your years, often carrying substantial responsibility from an early age. You build success through relentless persistence, and what you achieve in life is durable, hard-won, and respected.",
            "Early life may bring self-doubt, heavy burdens, or physical stiffness. Be patient with your timing, as Saturn's rewards flourish in the second half of life; take care of your joints, posture, and teeth, and cultivate warmth toward yourself.",
        ),
        2: (
            "You take a prudent, hard-working approach to building wealth and family security. You value saving, avoid waste, and earn through steady labor, traditional industries, land, or careful financial management.",
            "Speech can sometimes sound blunt, dry, or critical to sensitive family members. Ensure that financial caution does not turn into unnecessary penny-pinching, and cultivate warmth at the dinner table.",
        ),
        3: (
            "Your stamina, determination, and practical problem-solving skills are outstanding. You are not afraid of hard work, persevere through steep learning curves, and achieve long-term success through hands-on effort and discipline.",
            "Relations with siblings or peers may feel formal, distant, or burdened by obligation. Avoid taking on more than your fair share of responsibility, and celebrate small milestones along the way.",
        ),
        4: (
            "You build steady, lasting property and domestic security over time through patient effort. You have a deep sense of duty toward your family lineage, though early home life may have been disciplined, austere, or demanding.",
            "Emotional warmth in the domestic sphere can feel restrained, and you may find it difficult to fully unwind. Create cozy, relaxing rituals at home, and practice letting go of past domestic anxieties.",
        ),
        5: (
            "You possess a disciplined, serious intellect well suited for deep research, mathematics, engineering, or classical studies. You take commitments seriously and approach creative or pedagogical projects with methodical care.",
            "Romance may involve delays, caution, or practical considerations rather than light-hearted spontaneity. Classically, children may arrive later in life; be patient and avoid excessive worry over creative outcomes.",
        ),
        6: (
            "This is one of Saturn's strongest placements, granting tremendous capacity to overcome adversity, outwork competitors, and resolve long-standing problems. You excel in demanding service, law, administration, or industrial management.",
            "Do not ignore chronic minor physical symptoms, especially concerning joints, digestion, or fatigue. Maintain regular exercise routines, and avoid letting workplace duty crowd out basic rest and relaxation.",
        ),
        7: (
            "You take partnership and marriage with the utmost seriousness, seeking a loyal, dependable, and mature companion. Marriage may arrive later in life or with a noticeable age or maturity gap, but it tends to be lasting and stable.",
            "Relationships can suffer from emotional cool-down or viewing partnership purely as a set of duties. Inject regular playfulness, warmth, and appreciation into your bond to keep romance alive.",
        ),
        8: (
            "You possess great longevity, mental endurance, and the capacity to survive life's most intense crises with quiet composure. You can do well in research, long-term investments, auditing, or managing legacy matters.",
            "Matters of joint finances or inheritance can experience prolonged delays or administrative hurdles. Prioritize joint flexibility and chronic health care, and avoid dwelling on fatalistic thoughts.",
        ),
        9: (
            "You build your philosophical convictions and spiritual outlook through real-world experience rather than blind belief. Your luck unfolds gradually through consistent hard work, ethical discipline, and respect for tradition.",
            "Early relationships with father figures or teachers may feel strict or distant. Avoid cynicism regarding spiritual matters, and recognize that genuine wisdom requires an open, compassionate heart.",
        ),
        10: (
            "This is a powerhouse placement for long-term career achievement, executive responsibility, and public respect. You rise through merit, organize complex operations, and often achieve your highest career standing in mature adulthood.",
            "Early professional life can be demanding, with heavy responsibility and little immediate praise. Avoid shortcuts or bitterness; your steady climb leads to enduring authority that cannot easily be shaken.",
        ),
        11: (
            "Your ambitions materialize steadily over time, leading to durable financial gains and respected standing in organizations. You value long-term friendships with seasoned, reliable mentors and build wealth through patient compounding.",
            "Gains are rarely overnight; they require patience, consistent saving, and avoiding speculative get-rich-quick schemes. Ensure that your social circle includes people who bring joy and laughter into your life.",
        ),
        12: (
            "You have a natural capacity for solitude, disciplined spiritual practice, and selfless service behind the scenes. You can do well in international work, institutions, or remote settings where quiet dedication is needed.",
            "Watch for sleep disturbances, isolation, or carrying a vague sense of guilt or duty that does not belong to you. Keep your expenses organized, avoid debt, and prioritize peaceful, restorative sleep.",
        ),
    },
    "Rahu": {
        1: (
            "You possess magnetic charisma, sharp ambition, and an innovative, unconventional approach to life. You are drawn to modern ideas, technology, and cross-cultural experiences, and you have the ability to reinvent yourself to seize opportunities.",
            "An inner restlessness or identity confusion can cause you to wear different masks or chase illusions of grand success. Ground yourself in authentic values, avoid shortcuts, and protect your nervous system from chronic over-stimulation.",
        ),
        2: (
            "You are driven to acquire wealth through unconventional, modern, or international avenues. You have persuasive speech that can captivate audiences, and you think outside traditional boundaries when it comes to financial growth.",
            "Watch a tendency toward exaggerated speech or friction with family over unconventional choices. Maintain disciplined eating habits, and be transparent in financial dealings to avoid misunderstandings.",
        ),
        3: (
            "This is one of Rahu's best placements, giving bold initiative, media savvy, and fearlessness in taking calculated risks. You excel in digital media, technology, marketing, publishing, or entrepreneurship, staying ahead of emerging trends.",
            "Over-confidence or impulsive risk-taking can lead to occasional setbacks. Keep communications respectful with siblings and partners, and channel your restlessness into mastering cutting-edge skills.",
        ),
        4: (
            "You desire modern comforts, impressive properties, and a unique domestic environment, often in cosmopolitan or foreign settings. You are drawn to unconventional homes and seek to improve your family's material standing.",
            "Inner peace can be hard to sustain if you constantly seek external validation or property upgrades. Cultivate emotional grounding through meditation, and nurture warm, candid communication with your mother.",
        ),
        5: (
            "Your intelligence is sharp, non-traditional, and inventive, well suited for modern technology, coding, creative media, or unconventional strategies. You think outside the box and enjoy innovative creative pursuits.",
            "Speculative financial gambles can lead to sudden swings if driven by greed. In romance, avoid deceptive or confusing infatuations, and give children space to develop their own authentic paths.",
        ),
        6: (
            "A formidable placement for overcoming competition, outmanoeuvring rivals, and resolving complex challenges. You excel in competitive examinations, foreign litigation, technology, or dynamic service fields where boldness wins.",
            "Do not adopt questionable shortcuts to achieve victory, as they can backfire. Pay attention to mysterious or stress-related health symptoms promptly, and maintain a clean daily routine.",
        ),
        7: (
            "You are drawn to a partner from an unconventional, foreign, or distinctly different cultural or social background. You can achieve success in international business, public relations, and innovative partnerships.",
            "Unrealistic expectations or lack of transparency can create confusion in marriage. Choose partners with clear, open communication, and avoid idealizing someone before you truly know their character.",
        ),
        8: (
            "You have intense curiosity about the occult, cutting-edge research, forensic analysis, or unearned wealth. You have the ability to uncover hidden information and can benefit from sudden turns of fortune in technology or research.",
            "Avoid speculative or grey-area financial schemes, as sudden reversals can occur. Prioritize emotional and physical safety, drive cautiously, and stay grounded with trusted mentors.",
        ),
        9: (
            "You question conventional dogmas and are drawn to explore foreign philosophies, modern spirituality, and global journeys. You have an independent mind that seeks truth through personal experience rather than inherited tradition.",
            "Differences of opinion with father figures or traditional teachers can create friction. Cultivate respect for the roots of wisdom while exploring new horizons, and avoid cynical skepticism.",
        ),
        10: (
            "You have an intense hunger for professional prominence, social influence, and high status, often rising in technology, media, politics, or multinational organizations. You understand public psychology and can achieve rapid visibility.",
            "Sudden rises can be followed by sharp scrutiny if integrity is compromised. Protect your public reputation with rigorous ethics, and remember that lasting respect is built on character, not just visibility.",
        ),
        11: (
            "This is an extraordinarily powerful placement for large material gains, expansive networks, and fulfilling major ambitions. You connect with influential and diverse groups, leveraging modern platforms to achieve financial independence.",
            "Be vigilant against greed or associating with unscrupulous allies who offer easy riches. Ensure that your ambitions serve a genuine purpose beyond mere accumulation of prestige.",
        ),
        12: (
            "You have a strong affinity for foreign lands, international travel, and exploring esoteric or spiritual realms in private. You may settle far from your birthplace and find deep creative or spiritual breakthroughs in seclusion.",
            "Hidden expenditures, sleep disturbances, or escapist tendencies can drain your vitality. Establish a calm bedtime routine, keep financial bookkeeping meticulous, and avoid speculative ventures abroad.",
        ),
    },
    "Ketu": {
        1: (
            "You possess an intuitive, spiritual, and detached nature with deep inner insight. You see through superficial social pretences, have past-life wisdom, and are motivated by inner authenticity rather than outer acclaim.",
            "You may struggle with low self-assertion, feeling misunderstood, or experiencing uncertainty about your life direction. Ground yourself in physical activity, establish clear personal boundaries, and own your unique gifts.",
        ),
        2: (
            "You have a simple, unattached relationship with material wealth and conventional family prestige. You speak with raw, sometimes abrupt honesty, and you can achieve spiritual depth or expertise in esoteric knowledge.",
            "Income may fluctuate or feel unimportant to you, leading to occasional financial instability. Maintain structured financial habits for the sake of dependents, and soften your speech during family discussions.",
        ),
        3: (
            "You have quiet, unpretentious courage and strong research or technical capability. You work diligently without needing applause, excel in behind-the-scenes writing, coding, or investigative work, and possess deep mental focus.",
            "Relationships with siblings or peers can feel emotionally distant or detached. Practice expressing appreciation openly, and stay connected with your local community.",
        ),
        4: (
            "You experience a natural inner detachment from material real estate and conventional domestic comforts. You seek peace within your own mind rather than in external surroundings, and you often develop spiritual depth.",
            "A sense of rootlessness or emotional distance from maternal figures can leave you feeling unsettled. Create a quiet, sacred space at home for meditation, and practice active gratitude for domestic stability.",
        ),
        5: (
            "You have intuitive, non-linear intelligence with a natural gift for mantra, spiritual wisdom, psychology, or abstract mathematics. You possess past-life insights and look beneath surface appearances in intellectual matters.",
            "In romance, you may feel detached or easily disillusioned when the initial spark fades. Give children patient, practical guidance without being aloof, and rely on structured analysis for financial choices.",
        ),
        6: (
            "You have the capacity to quietly overcome obstacles, outlast difficulties, and heal others through alternative or intuitive methods. You are not intimidated by opposition and can do meaningful work in research or service.",
            "Pay attention to vague or hard-to-diagnose health symptoms, especially regarding immunity or gut health. Maintain regular hygiene and nutrition, and avoid ignoring bodily needs.",
        ),
        7: (
            "You are drawn to a partner who is spiritual, introspective, or unconventional in outlook. Marriage teaches you that true partnership is a union of souls that requires mutual understanding beyond material expectations.",
            "Emotional detachment, disinterest in routine domestic life, or misunderstandings can create distance in marriage. Make conscious effort to share warmth, engage in everyday conversations, and express affection regularly.",
        ),
        8: (
            "This is a profound placement for mystical insight, occult research, psychological transformation, and spiritual awakening. You have the ability to read beneath the surface of reality and navigate life's mysteries with equanimity.",
            "Be cautious with sudden health matters, and maintain regular medical check-ups. Keep clear documentation in joint financial and inheritance matters, and ground your esoteric interests in practical living.",
        ),
        9: (
            "You possess an innate spiritual wisdom that looks beyond rigid dogmas and rituals to the universal core of truth. You are an independent seeker of higher knowledge, comfortable studying ancient philosophies on your own terms.",
            "You may question traditional teachers or religious authorities to the point of isolation. Honor the value of established frameworks while pursuing your personal path of direct spiritual insight.",
        ),
        10: (
            "You perform your professional duties with dedication and skill without being attached to applause or status. You excel in technical, research, analytical, or spiritual professions where quiet competence is required.",
            "A sense of dissatisfaction with conventional career success can cause you to change roles abruptly. Find work that aligns with your deeper values so your competence is channelled into meaningful outcomes.",
        ),
        11: (
            "Financial gains and opportunities often arrive unexpectedly rather than through conventional networking. You prefer a small circle of authentic, spiritually grounded friends and feel detached from superficial social circles.",
            "You may feel indifferent to your accomplishments or struggle to celebrate your wins. Acknowledge your progress, and direct surplus resources toward meaningful charitable causes.",
        ),
        12: (
            "This is Ketu's most celebrated placement (Moksha karaka), bestowing spiritual liberation, deep meditative insight, and freedom from material bondage. You find your highest peace in solitary contemplation, sacred places, or selfless service.",
            "Ensure that spiritual detachment does not turn into practical neglect of your health, sleep, or daily responsibilities. Balance your inner sanctuary with grounded presence in the everyday world.",
        ),
    },
}

DIGNITY_NOTE: dict[str, str] = {
    "exalted": "Because it is in its sign of exaltation, this planet operates with its highest potency, clarity, and grace. Its gifts manifest reliably and lift the areas of life it touches.",
    "moolatrikona": "Placed in its moolatrikona sign, the planet is on its home ground with strong confidence and purpose, giving steady, high-quality results throughout life.",
    "own": "In its own sign, the planet is completely comfortable, protective, and resourceful. It guards the houses it rules and brings stability to its significations.",
    "friendly": "Sitting in a friendly sign, the planet finds receptive soil. Its results flow naturally with moderate effort and goodwill from surrounding circumstances.",
    "neutral": "In a neutral sign, the planet acts as a fair judge. Its results depend closely on its house placement, aspects, and the strength of its dispositor.",
    "enemy": "In an uncomfortable enemy's sign, the planet faces resistance. Its constructive side still functions, but requires greater conscious discipline and patience.",
    "debilitated": "In its sign of debilitation, the planet's natural expression is strained or inverted. The cautions listed require extra mindfulness, and supportive remedies bring significant balance.",
}

HOUSE_PLAIN: dict[int, str] = {
    1: "your physical vitality, personal presence, self-confidence and overall life direction",
    2: "earned wealth, family heritage, food habits and the power of your spoken word",
    3: "courage, personal initiative, creative skills, siblings and short journeys",
    4: "home life, mother, property, vehicles and emotional peace of mind",
    5: "creative intelligence, progeny, past merit, higher judgment and romantic instincts",
    6: "workplace routine, health resistance, managing competition, debts and service",
    7: "marriage, life partner, business partnerships and public collaborations",
    8: "longevity, deep transformation, research, joint finances and unexpected events",
    9: "fortune, father, ethical principles, higher learning and spiritual guidance",
    10: "career standing, leadership authority, public reputation and life contribution",
    11: "steady income, social networks, realization of ambitions and supportive allies",
    12: "expenses, foreign travel, restorative solitude, sleep and spiritual liberation",
}


def house_meaning(n: int, score: int, lord: str, lord_house: int, occupants: list[str]) -> str:
    area = HOUSE_PLAIN[n]
    if score >= 70:
        lead = (f"This area of your life — governing {area} — stands as a primary strength in your Kundli. "
                "Conditions here are supportive, allowing you to build lasting results with confidence.")
    elif score >= 55:
        lead = (f"This area of life — {area} — is generally stable and cooperative. "
                "Progress unfolds steadily with consistent, disciplined effort.")
    elif score >= 45:
        lead = (f"This area — governing {area} — carries a balanced mix of opportunity and growth lessons. "
                "Some aspects will thrive naturally, while others reward patience and thoughtful planning.")
    else:
        lead = (f"This area of life — {area} — invites conscious care and dedication. "
                "Early challenges or delays here are designed to develop resilience, and remedies help smooth the way.")

    target_theme = HOUSE_PLAIN[lord_house].split(" — ")[0].split(",")[0]
    link = f" Because its governing planet ({lord}) is situated in the domain of {target_theme}, the outcomes here are intimately tied to how you handle that part of your life."
    occ = ""
    if occupants:
        occ = f" The presence of {', '.join(occupants)} directly colours the atmosphere here with their energetic qualities."
    return lead + link + occ


DOSHA_PLAIN: dict[str, tuple[str, str]] = {
    "Manglik (Kuja) Dosha": (
        "Mars occupies a sensitive relationship angle in your chart (such as the 1st, 2nd, 4th, 7th, 8th or 12th house). This infuses partnerships with high passion, directness, and drive, but can also trigger impatience, hasty reactions, or arguments when individual wills clash.",
        "Classical texts advise pairing with another Manglik partner or waiting until emotional maturity develops (around age 28). Practising calm communication, allowing each other personal space, and chanting Hanuman Chalisa or Mars mantras on Tuesdays help harmonize this fire.",
    ),
    "Kaal Sarp Dosha": (
        "All seven classical planets are hemmed on one side of the karmic Rahu–Ketu nodal axis. In everyday experience, this pattern can make life feel like a series of dramatic surges and pauses, where effort takes time to bear fruit and major milestones occur through sudden turning points.",
        "Kaal Sarp does not deny high achievement—many world leaders, innovators, and entrepreneurs have it. The golden rule is to avoid risky shortcuts, maintain ethical discipline, and perform traditional remedies like Maha Mrityunjaya Japa or pilgrimage to Trimbakeshwar or Ujjain.",
    ),
    "Pitra Dosha": (
        "This signature reflects unresolved ancestral karma or an afflicted 9th house/Sun axis. It often shows up as recurring obstacles in family matters, delays in major milestones, or challenges related to the father, lineage, or prosperity that appear without an obvious external reason.",
        "Traditional Vedic wisdom recommends honoring departed ancestors during Pitru Paksha, performing Tarpan on Amavasya (new moon), feeding cows or needy individuals, and respecting parents and mentors with genuine reverence.",
    ),
    "Shani Dosha / Sade Sati": (
        "Saturn is transiting the sensitive 12th, 1st, or 2nd house from your natal Moon sign across a 7½-year cycle. This is a profound maturation phase that asks for patience, streamlined responsibilities, and unhurried effort, often accompanied by heavier duties or health awareness.",
        "Sade Sati is not a curse—it is a masterclass in maturity and builds rock-solid resilience. Avoid reckless speculation, maintain a quiet daily routine, respect labor and service staff, and light a sesame-oil lamp under a sacred Peepal tree on Saturdays.",
    ),
    "Grahan Dosha": (
        "The luminary of soul (Sun) or mind (Moon) is joined by one of the shadowy lunar nodes (Rahu or Ketu). This combination can bring occasional phases of self-doubt, identity questions, or fluctuating confidence when under pressure.",
        "Daily grounding through meditation, regular exposure to morning sunlight, pranayama, and chanting the Gayatri or Shiva mantra steady the mental waters and help your true inner light shine brightly.",
    ),
}

YOGA_CATEGORY_PLAIN: dict[str, str] = {
    "Pancha Mahapurusha": "an elite classical hallmark of leadership and mastery; the planet involved bestows an exceptional talent that elevates your status and character",
    "Lunar": "a powerful blessing for emotional stability, intuitive intelligence, and how warmly the public and peers respond to you",
    "Solar": "a mark of self-confidence, professional authority, and supportive connections with government or executive figures",
    "Raja": "a royal combination linking purposeful action with fortune; it grants rise in status, authority, and public respect, particularly during the dashas of the participating planets",
    "Wealth": "an auspicious wealth configuration that supports steady income, asset building, and material prosperity over the course of life",
    "Dhana": "a dedicated prosperity signature that fosters financial acumen, disciplined savings, and multiple channels of revenue",
    "Fame": "a signature of honor and unblemished reputation, ensuring that your work is recognized and valued by society",
    "Learning": "a high blessing for academic excellence, articulate expression, wisdom, and mastery across the arts or sciences",
}


def yoga_meaning(category: str, name: str) -> str:
    base = YOGA_CATEGORY_PLAIN.get(category, "it adds a distinct strength and protective grace to your Kundli")
    return (f"In practical terms, {name} represents {base}. Vedic combinations give their fullest fruits "
            f"when the planets that form them run their corresponding Mahadasha and Antardasha periods.")


def dasha_plain(lord: str, tone: str, houses: list[int]) -> str:
    areas = ", ".join(HOUSE_PLAIN[h].split(" — ")[0].split(",")[0] for h in houses[:3])
    feel = {
        "excellent": "This is one of the most productive, rewarding chapters in your chart's timeline",
        "favourable": "Overall, this is an encouraging and supportive phase for steady progress",
        "mixed": "This chapter brings a dynamic combination of opportunity and character-building lessons",
        "challenging": "This period calls for patience, measured choices, and deliberate care",
    }.get(tone, "This period initiates significant change and growth")
    return (f"{feel}. The primary momentum of your life shifts toward {areas}. "
            f"Use this window to take strategic, ethical steps in these domains, and refer to the cautions to steer clear of avoidable missteps.")
