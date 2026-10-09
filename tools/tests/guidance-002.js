const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const vc = new VirtualConsole(); const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

const S = 2, LO = 1, HI = 157;        // verses authored so far
const LAST = 286;                      // verses in the surah

(async () => {
  const dom = await JSDOM.fromURL('http://127.0.0.1:8000/', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (i, o) => fetch(new URL(i, 'http://127.0.0.1:8000/'), o);
      w.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, onchange: null });
    }
  });
  const w = dom.window;
  await new Promise(r => w.addEventListener('load', r, { once: true }));
  await new Promise(r => setTimeout(r, 800));
  const R = []; const ck = (n, c, d) => R.push({ n, ok: !!c, d: d === undefined ? '' : String(d) });

  const PLAN = await (await fetch('http://127.0.0.1:8000/data/plan.json')).json();
  await w.eval(`Promise.all([loadTafsirData(${S}), loadGuidanceData(${S})])`);

  ck(`guidance_${String(S).padStart(3,'0')} loads`, await w.eval(`!!loadedGuidance[${S}]`));
  ck(`covers exactly verses ${LO}-${HI}`,
     w.eval(`Object.keys(loadedGuidance[${S}].verses).join(',')`) === Array.from({length: HI-LO+1}, (_,i)=>LO+i).join(','),
     w.eval(`Object.keys(loadedGuidance[${S}].verses).join(',')`));
  ck('every entry has a correct range', w.eval(`Object.entries(loadedGuidance[${S}].verses).every(([a,v])=>v.range==="${S}:"+a)`));
  ck('every entry records 5+ sources drawn on', w.eval(`Object.values(loadedGuidance[${S}].verses).every(v=>v.draws_on.length>=5)`));
  ck('all draws_on ids are real sources', w.eval(`Object.values(loadedGuidance[${S}].verses).every(v=>v.draws_on.every(id=>loadedTafsir[${S}].sources.some(s=>s.id===id)))`));

  for (let a = LO; a <= HI; a++) {
    const n = w.eval(`loadedGuidance[${S}].verses["${a}"].text.trim().split(/\\s+/).length`);
    const tgt = PLAN[`${S}:${a}`].words;
    // The plan target is a FLOOR, not a band. A verse may run long; it must
    // not run short. Set by the maintainer 2026-10-09, reversing the earlier
    // two-sided 25% tolerance.
    const floor = Math.round(tgt * 0.75);
    ck(`${S}:${a} length ${n}w meets the floor (${floor}w of ${tgt}w, Tier ${PLAN[`${S}:${a}`].tier})`,
       n >= floor, `${n} vs floor ${floor}`);
  }

  // ---------- quotes the app's own translation ----------
  await w.eval(`loadChapterData(${S})`);
  const pairs = [
    [1, 'Alif-Lãm-Mĩm'],
    [2, 'This is the Book'], [2, 'no doubt about it'], [2, 'mindful'],
    [3, 'the unseen'], [3, 'establish prayer'], [3, 'what We have provided'],
    [4, 'revealed before you'], [4, 'sure faith in the Hereafter'],
    [5, 'guided by their Lord'], [5, 'successful'],
    [6, 'persist in disbelief'], [6, 'whether you warn them or not'],
    [7, 'sealed their hearts'], [7, 'sight is covered'], [7, 'tremendous punishment'],
    [8, 'We believe in Allah and the Last Day'], [8, 'not ˹true˺ believers'],
    [9, 'deceive Allah and the believers'], [9, 'only deceive themselves'], [9, 'fail to perceive'],
    [10, 'sickness in their hearts'], [10, 'lets their sickness increase'], [10, 'painful punishment'],
    [11, 'Do not spread corruption in the land'], [11, 'peace-makers'],
    [12, 'they who are the corruptors'],
    [13, 'Believe as others believe'], [13, 'as the fools believe'], [13, 'they who are fools'],
    [14, 'When they meet the believers'], [14, 'evil associates'], [14, 'we were only mocking'],
    [15, 'throw their mockery back at them'], [15, 'wandering blindly in their defiance'],
    [16, 'trade guidance for misguidance'], [16, 'this trade is profitless'],
    [17, 'someone who kindles a fire'], [17, 'Allah takes away their light'], [17, 'unable to see'],
    [18, 'deaf, dumb, and blind'], [18, 'they will never return'],
    [19, 'a rainstorm from the sky'], [19, 'thunder, and lightning'], [19, 'for fear of death'],
    [19, 'Allah encompasses the disbelievers'],
    [20, 'the lightning were about to snatch away their sight'], [20, 'when darkness covers them'],
    [20, 'Most Capable of everything'],
    [21, 'O humanity'], [21, 'Worship your Lord'], [21, 'created you and those before you'],
    [22, 'earth a place of settlement'], [22, 'the sky a canopy'], [22, 'causing fruits to grow'],
    [22, 'do not knowingly set up equals'],
    [23, 'if you are in doubt'], [23, 'produce a sûrah like it'], [23, 'call your helpers'],
    [24, 'you will never be able to do so'], [24, 'fuelled with people and stones'],
    [25, 'Give good news'], [25, 'Gardens under which rivers flow'], [25, 'This is what we were given before'],
    [25, 'pure spouses'],
    [26, 'does not shy away from using the parable of a mosquito'], [26, 'What does Allah mean by such a parable'],
    [26, 'except the rebellious'],
    [27, "violate Allah's covenant"], [27, 'ordered to be maintained'], [27, 'spread corruption in the land'],
    [27, 'the true losers'],
    [28, 'How can you deny Allah'], [28, 'You were lifeless and He gave you life'],
    [28, 'again bring you to life'], [28, 'to Him you will'],
    [29, 'created everything in the earth for you'], [29, 'seven heavens'], [29, 'knowledge of all things'],
    [30, 'successive'], [30, 'authority on earth'], [30, 'spread corruption there and shed blood'],
    [30, 'glorify Your praises'], [30, 'I know what you do not know'],
    [31, 'He taught Adam the names of all things'], [31, 'presented them to the angels'],
    [31, 'Tell Me the names of these'],
    [32, 'Glory be to You'], [32, 'no knowledge except what You have taught us'],
    [32, 'All-Knowing, All-Wise'],
    [33, 'Inform them of their names'], [33, 'secrets of the heavens and the earth'],
    [33, 'what you reveal and what you conceal'],
    [34, 'Prostrate before Adam'], [34, 'not Iblîs'], [34, 'refused and acted arrogantly'],
    [35, 'Live with your wife in Paradise'], [35, 'eat as freely as you please'],
    [35, 'do not approach this tree'], [35, 'you will be wrongdoers'],
    [36, 'Satan deceived them'], [36, 'fall from the'], [36, 'Descend from the heavens'],
    [36, 'enemies to each other'], [36, 'a residence and provision'],
    [37, 'inspired with words'], [37, 'accepted his repentance'], [37, 'Accepter of Repentance'],
    [38, 'Descend all of you'], [38, 'when guidance comes to you from Me'],
    [38, 'no fear for them, nor will they grieve'],
    [39, 'those who disbelieve and deny Our signs'], [39, 'residents of the Fire'],
    [39, 'They will be there forever'],
    [40, 'O children of Israel'], [40, 'Remember My favours upon you'],
    [40, 'Fulfil your covenant'], [40, 'stand in awe of Me'],
    [41, 'Believe in My revelations'], [41, 'confirm your Scriptures'],
    [41, 'first to deny them'], [41, 'a fleeting gain'], [41, 'be mindful of Me'],
    [42, 'mix truth with falsehood'], [42, 'hide the truth knowingly'],
    [43, 'Establish prayer'], [43, 'pay alms-tax'], [43, 'bow down with those who bow down'],
    [44, 'preach righteousness'], [44, 'fail to practice it yourselves'],
    [44, 'you read the Scripture'], [44, 'Do you not understand'],
    [45, 'seek help through patience and prayer'], [45, 'it is a burden'],
    [45, 'except for the humble'],
    [46, 'certain that they will meet their Lord'], [46, 'to Him they will return'],
    [47, 'Remember'], [47, 'favours I granted you'], [47, 'I honoured you above the others'],
    [48, 'Guard yourselves against the Day'], [48, 'no soul will be of help to another'],
    [48, 'No intercession will be accepted'], [48, 'no ransom taken'], [48, 'no help will be given'],
    [49, 'how We delivered you from the people of Pharaoh, who afflicted you with dreadful torment, slaughtering your sons and keeping your women. That was a severe test from your Lord'],
    [50, 'when We parted the sea, rescued you, and drowned'],
    [50, 'people before your very eyes'],
    [51, 'when We appointed forty nights for Moses, then you worshipped the calf in his absence, acting wrongfully'],
    [52, 'so perhaps you would be grateful'],
    [53, 'when We gave Moses the Scripture—the standard'],
    [53, 'to distinguish between right and wrong'],
    [53, 'that perhaps you would be'],
    [54, 'my people! Surely you have wronged yourselves by worshipping the calf, so turn in repentance to your Creator and execute'],
    [54, 'Then He accepted your repentance. Surely He is the Accepter of Repentance, Most Merciful'],
    [54, 'yourselves. That is best for you in the sight of your'],
    [55, 'Moses! We will never believe you until we see Allah with our own'],
    [55, 'so a thunderbolt struck you while you were looking on'],
    [56, 'Then We brought you back to life after your death, so that perhaps you would be grateful'],
    [57, 'We shaded you with clouds and sent down to you manna and'],
    [57, 'from the good things We have provided for'],
    [57, 'did not wrong Us, but wronged themselves'],
    [58, 'this city and eat freely from wherever you please; enter the gate with humility, saying'],
    [58, 'We will forgive your sins and multiply the reward for the'],
    [59, 'But the wrongdoers changed the words they were commanded to say. So We sent down a punishment from the heavens upon them for their rebelliousness'],
    [60, 'provisions, and do not go about spreading corruption in the'],
    [60, 'when Moses prayed for water for his people, We said'],
    [60, 'each tribe knew its drinking place'],
    [61, 'call upon your Lord on our behalf, He will bring forth for us some of what the earth produces of herbs, cucumbers, garlic, lentils, and'],
    [61, 'They were stricken with disgrace and misery, and they invited the displeasure of Allah for rejecting'],
    [61, 'go down to any village and you will find what you have asked'],
    [62, 'believes in Allah and the Last Day and does good will have their reward with their Lord. And there will be no fear for them, nor will they grieve'],
    [62, 'Indeed, the believers, Jews, Christians, and'],
    [63, 'which We have given you and observe its teachings so perhaps you will become mindful'],
    [63, 'when We took a covenant from you and raised the mountain above you'],
    [64, 'grace and mercy upon you, you would have certainly been of the losers'],
    [64, 'Yet you turned away afterwards. Had it not been for'],
    [65, 'You are already aware of those of you who broke the Sabbath. We said to them'],
    [66, 'So We made their fate an example to present and future generations, and a lesson to the God-fearing'],
    [67, 'seek refuge in Allah from acting'],
    [67, 'when Moses said to his people'],
    [67, 'commands you to sacrifice a'],
    [68, 'cow should neither be old nor young but in between. So do as you are'],
    [68, 'upon your Lord to clarify for us what type'],
    [69, 'should be a bright yellow cow—pleasant to'],
    [69, 'upon your Lord to specify for us its'],
    [70, 'upon your Lord so that He may make clear to us which cow, for all cows look the same to us. Then, Allah willing, we will be guided'],
    [71, 'should have been used neither to till the soil nor water the fields; wholesome and without'],
    [71, 'Yet they still slaughtered it hesitantly'],
    [71, 'you have come with the'],
    [72, 'when a man was killed and you disputed who the killer was, but Allah revealed what you concealed'],
    [73, 'Allah brings the dead to life, showing you His signs so that you may understand'],
    [73, 'the dead body with a piece of the'],
    [74, 'Even then your hearts became hardened like a rock or even harder, for some rocks gush rivers; others split, spilling water; while others are humbled in awe of Allah. And Allah is never unaware of what you do'],
    [75, 'expect them to be true to you, though a group of them would hear the word of Allah then knowingly corrupt it after understanding it'],
    [76, 'you disclose to the believers the knowledge Allah has revealed to'],
    [76, 'that they may use it against you before your Lord? Do you not'],
    [76, 'When they meet the believers they say'],
    [77, 'Do they not know that Allah is aware of what they conceal and what they reveal'],
    [78, 'And among them are the illiterate who know nothing about the Scripture except lies, and'],
    [79, 'a fleeting gain! So woe to them for what their hands have written, and woe to them for what they have earned'],
    [79, 'those who distort the Scripture with their own hands then say'],
    [80, 'you taken a pledge from Allah—for Allah never breaks His word—or are you'],
    [80, 'Fire will not touch us except for a number of'],
    [80, 'saying about Allah what you do not'],
    [81, 'But no! Those who commit evil and are engrossed in sin will be the residents of the Fire. They will be there forever'],
    [82, 'And those who believe and do good will be the residents of Paradise. They will be there forever'],
    [83, 'none but Allah; be kind to parents, relatives, orphans and the needy; speak kindly to people; establish prayer; and pay'],
    [83, 'turned away—except for a few of you—and were indifferent'],
    [83, 'when We took a covenant from the children of Israel'],
    [84, 'blood nor expel each other from their homes, you gave your pledge and bore witness'],
    [84, 'when We took your covenant that you would neither shed each'],
    [85, 'you believe in some of the Scripture and reject the rest? Is there any reward for those who do so among you other than disgrace in this worldly life and being subjected to the harshest punishment on the Day of Judgment? For Allah is never unaware of what you do'],
    [85, 'But here you are, killing each other and expelling some of your people from their homes, aiding one another in sin and aggression; and when those'],
    [85, 'come to you as captives, you still ransom them—though expelling them was unlawful for'],
    [86, 'These are the ones who trade the Hereafter for the life of this world. So their punishment will not be reduced, nor will they be helped'],
    [87, 'Indeed, We gave Moses the Book and sent after him successive messengers. And We gave Jesus, son of Mary, clear proofs and supported him with the holy'],
    [87, 'with something you do not like, you become arrogant, rejecting some and killing others'],
    [87, 'is it that every time a messenger comes to you'],
    [88, 'fact, Allah has condemned them for their disbelief. They have but little faith'],
    [89, 'there came to them a Book from Allah which they'],
    [89, 'Although they used to pray for victory'],
    [89, 'condemnation be upon the disbelievers'],
    [90, 'revelation and resenting Allah for granting His grace to whoever He wills of His servants! They have earned wrath upon wrath. And such disbelievers will suffer a humiliating punishment'],
    [90, 'Miserable is the price they have sold their souls for—denying'],
    [91, 'and they deny what came afterwards, though it is the truth confirming their own Scriptures! Ask'],
    [91, 'only believe in what was sent down to'],
    [91, 'prophets before, if you are'],
    [92, 'Indeed, Moses came to you with clear proofs, then you worshipped the calf in his absence, acting wrongfully'],
    [93, 'The love of the calf was rooted in their hearts because of their disbelief. Say'],
    [93, 'And when We took your covenant and raised the mountain above you'],
    [93, 'belief prompts you to do, if you'],
    [94, 'out of all humanity, then wish for death if what you say is'],
    [94, 'Home of the Hereafter with Allah is exclusively for you'],
    [95, 'But they will never wish for that because of what their hands have'],
    [95, 'knowledge of the wrongdoers'],
    [96, 'You will surely find them clinging to life more eagerly than any other people, even more than polytheists. Each one of them wishes to live a thousand years. But even if they were to live that long, it would not save them from the punishment. And Allah is All-Seeing of what they do'],
    [97, 'Will, confirming what came before it—a guide and good news for the'],
    [97, 'is an enemy of Gabriel should know that he revealed this'],
    [98, 'Whoever is an enemy of Allah, His angels, His messengers, Gabriel, and Michael, then'],
    [98, 'Allah is certainly the enemy of the disbelievers'],
    [98, 'let them know that'],
    [99, 'none will deny them except the rebellious'],
    [99, 'Indeed, We have sent down to you'],
    [100, 'Why is it that every time they make a covenant, a group of them casts it aside? In fact, most of them do not believe'],
    [101, 'Now, when a messenger from Allah has come to them—confirming their own Scriptures—some of the People of the Book cast the Book of Allah behind their backs as if they did not know'],
    [102, 'followed the magic promoted by the devils during the reign of Solomon. Never did Solomon disbelieve, rather the devils disbelieved. They taught magic to the people, along with what had been revealed to the two angels, Hârût and Mârût, in'],
    [102, 'Will. They learned what harmed them and did not benefit them—although they already knew that whoever buys into magic would have no share in the Hereafter. Miserable indeed was the price for which they sold their souls, if only they knew'],
    [102, 'between husband and wife; although their magic could not harm anyone except by'],
    [103, 'there would have been a better reward from Allah, if only they knew'],
    [103, 'If only they were faithful and mindful'],
    [104, 'the disbelievers will suffer a painful punishment'],
    [104, '[Tend to us!] and listen'],
    [104, 'O believers! Do not say'],
    [105, 'The disbelievers from the People of the Book and the polytheists would not want you to receive any blessing from your Lord, but Allah selects whoever He wills for His mercy. And Allah is the Lord of infinite bounty'],
    [106, 'verse or cause it to be forgotten, We replace it with a better or similar one. Do you not know that Allah is Most Capable of everything'],
    [107, 'Do you not know that the kingdom of the heavens and the earth belongs'],
    [107, 'to Allah, and you have no guardian or helper besides Allah'],
    [108, 'whoever trades belief for disbelief has truly strayed from the Right Way'],
    [108, 'intend to ask of your Messenger as Moses was asked'],
    [109, 'back to disbelief because of their envy, after the truth has been made clear to them. Pardon and bear with them until Allah delivers His decision. Surely Allah is Most Capable of everything'],
    [109, 'Many among the People of the Book wish they could turn you'],
    [110, 'Establish prayer, and pay alms-tax. Whatever good you send forth for yourselves, you will'],
    [110, 'with Allah. Surely Allah is All-Seeing of what you do'],
    [111, 'The Jews and Christians each claim that none will enter Paradise except those of their own faith. These are their desires. Reply'],
    [111, 'your proof if what you say is'],
    [112, 'But no! Whoever submits themselves to Allah and does good will have their reward with their Lord. And there will be no fear for them, nor will they grieve'],
    [113, 'Surely Allah will judge between them on the Day of Judgment regarding their dispute'],
    [113, 'although both recite the Scriptures. And those'],
    [113, 'who have no knowledge say the same'],
    [114, 'Name from being mentioned in His places of worship and strive to destroy them? Such people have no right to enter these places except with'],
    [114, 'them is disgrace in this world, and they will suffer a tremendous punishment in the Hereafter'],
    [114, 'Who does more wrong than those who prevent'],
    [115, 'To Allah belong the east and the west, so wherever you turn you are facing'],
    [116, 'be to Him! In fact, to Him belongs whatever is in the heavens and the earth—all are subject to His Will'],
    [117, 'the Originator of the heavens and the earth! When He decrees a matter, He simply tells it'],
    [118, 'The same was said by those who came before. Their hearts are all alike. Indeed, We have made the signs clear for people of sure faith'],
    [118, 'only Allah would speak to us or a sign would come to'],
    [118, 'Those who have no knowledge say'],
    [119, 'as a deliverer of good news and a warner. And you will not be accountable for the residents of the Hellfire'],
    [119, 'We have surely sent you with the truth'],
    [120, 'the knowledge that has come to you, there would be none to protect or help you against Allah'],
    [120, 'Never will the Jews or Christians be pleased with you, until you follow their faith. Say'],
    [120, 'And if you were to follow their desires after'],
    [121, 'Those We have given the Book follow it as it should be followed. It is they who'],
    [121, 'believe in it. As for those who reject it, it is they who are the losers'],
    [122, 'O Children of Israel! Remember My favours upon you and how I honoured you above the others'],
    [123, 'And guard yourselves against the Day when no soul will be of any help to another. No ransom will be taken, no intercession accepted, and no help will be given'],
    [124, 'will certainly make you into a role model for the'],
    [124, 'commandments, which he fulfilled. Allah said'],
    [124, 'when Abraham was tested by his Lord with'],
    [125, 'And We entrusted Abraham and Ishmael to purify My House for those who circle it, who meditate in it, and who bow and prostrate themselves'],
    [125, 'centre and a sanctuary for the people'],
    [125, 'take the standing-place of'],
    [126, 'for those who disbelieve, I will let them enjoy themselves for a little while, then I will condemn them to the torment of the Fire. What an evil'],
    [126, 'secure and provide fruits to its people—those among them who believe in Allah and the Last'],
    [126, 'Lord, make this city'],
    [127, 'when Abraham raised the foundation of the House with Ishmael'],
    [127, 'from us. You are indeed the All-Hearing, All-Knowing'],
    [128, 'Show us our rituals, and turn to us in grace. You are truly the Accepter of Repentance, Most Merciful'],
    [128, 'from our descendants a nation that will submit to'],
    [128, 'Our Lord! Make us both'],
    [129, 'Our Lord! Raise from among them a messenger who will recite to them Your revelations, teach them the Book and wisdom, and purify them. Indeed, You'],
    [130, 'And who would reject the faith of Abraham except a fool! We certainly chose him in this life, and in the Hereafter he will surely be among the righteous'],
    [131, 'When his Lord ordered him'],
    [131, 'submit to the Lord of all'],
    [132, 'This was the advice of Abraham—as well as Jacob—to his children'],
    [132, 'Allah has chosen for you this faith; so do not die except in'],
    [133, 'worship your God, the God of your forefathers—Abraham, Ishmael, and Isaac—the One God. And to Him we'],
    [133, 'Or did you witness when death came to Jacob? He asked his children'],
    [133, 'will you worship after my'],
    [134, 'That was a community that had already gone before. For them is what they earned and for you is what you have earned. And you will not be accountable for what they have done'],
    [135, 'We follow the faith of Abraham, the upright—who was not a'],
    [135, 'The Jews and Christians each say'],
    [136, 'believe in Allah and what has been revealed to us; and what was revealed to Abraham, Ishmael, Isaac, Jacob, and his descendants; and what was given to Moses, Jesus, and other prophets from their Lord. We make no distinction between any of them. And to Allah we all'],
    [137, 'But Allah will spare you their evil. For He is the All-Hearing, All-Knowing'],
    [137, 'So if they believe in what you believe, then they will indeed be'],
    [137, 'guided. But if they turn away, they are simply opposed'],
    [138, 'Way of Allah. And who is better than Allah in ordaining a way? And we worship'],
    [139, 'you dispute with us about Allah, while He is our Lord and your Lord? We are accountable for our deeds and you for yours. And we are devoted to Him'],
    [140, 'Who does more wrong than those who hide the testimony they received from Allah? And Allah is never unaware of what you do'],
    [140, 'Do you claim that Abraham, Ishmael, Isaac, Jacob, and his descendants were all Jews or'],
    [140, 'is more knowledgeable: you or'],
    [141, 'That was a community that had already gone before. For them is what they earned and for you is what you have earned. And you will not be accountable for what they have done'],
    [142, 'did they turn away from the direction of prayer they used to'],
    [142, 'to Allah. He guides whoever He wills to the Straight'],
    [142, 'The foolish among the people will ask'],
    [143, 'so that you may be witnesses over humanity and that the Messenger may be a witness over you. We assigned your former direction of prayer only to distinguish those who would remain faithful to the Messenger from those who would lose faith. It was certainly a difficult test except for those'],
    [143, 'faith. Surely Allah is Ever Gracious and Most Merciful to humanity'],
    [143, 'guided by Allah. And Allah would never discount your'],
    [144, 'you are, turn your faces towards it. Those who were given the Scripture certainly know this to be the truth from their Lord. And Allah is never unaware of what they do'],
    [144, 'turning your face towards heaven. Now We will make you turn towards a direction'],
    [144, 'that will please you. So turn your face towards the Sacred Mosque'],
    [145, 'Even if you were to bring every proof to the People of the Book, they would not accept your direction'],
    [145, 'the knowledge that has come to you, then you would certainly be one of the wrongdoers'],
    [145, 'nor would you accept theirs; nor would any of them accept the direction'],
    [146, 'as they recognize their own children. Yet a group of them hides the truth knowingly'],
    [146, 'Those We have given the Scripture recognize this'],
    [147, 'the truth from your Lord, so do not ever be one of those who doubt'],
    [148, 'So compete with one another in doing good. Wherever you are, Allah will bring you all together'],
    [148, 'Surely Allah is Most Capable of everything'],
    [148, 'Everyone turns to their own direction'],
    [149, 'turn your face towards the Sacred Mosque. This is certainly the truth from your Lord. And Allah is never unaware of what you'],
    [150, 'are, face towards it, so that people will have no argument against you, except the wrongdoers among them. Do not fear them; fear Me, so that I may'],
    [150, 'turn your face towards the Sacred Mosque. And wherever you'],
    [150, 'perfect My favour upon you and so you may be'],
    [151, 'Since We have sent you a messenger from among yourselves—reciting to you Our revelations, purifying you, teaching you the Book and wisdom, and teaching you what you never knew—'],
    [152, 'Me; I will remember you. And thank Me, and never be ungrateful'],
    [153, 'O believers! Seek comfort in patience and prayer. Allah is truly with those who are patient'],
    [154, 'Never say that those martyred in the cause of Allah are dead—in fact, they are alive! But you do not perceive it'],
    [155, 'We will certainly test you with a touch of fear and famine and loss of property, life, and crops. Give good news to those who patiently endure—'],
    [156, 'to Allah we belong and to Him we will'],
    [156, 'when faced with a disaster, say'],
    [157, 'blessings and mercy. And it is they who are'],
    [157, 'They are the ones who will receive'],
  ];
  for (const [a, frag] of pairs) {
    ck(`${S}:${a} quotes the translation "${frag}"`, w.eval(`loadedGuidance[${S}].verses["${a}"].text`).includes(frag));
  }

  // ---------- integrity: named authorities must appear in that verse's sources ----------
  // Narrators and collectors only. The six tafsir TITLES are verified separately
  // against the payload's labels — a work does not cite itself in its own body.
  const NAMES = ['Al-Qurṭubī', 'Imām Aḥmad', 'Muslim', 'at-Tirmidhī',
    'an-Nasāʾī', 'Ibn Mājah', 'Al-Bukhārī', 'Abū Hurayrah', 'Ibn Masʿūd', 'al-Ḥākim',
    'Ad-Dārimī', 'ash-Shaʿbī', 'aṭ-Ṭabarānī', 'Ibn Ḥibbān', 'Ibn Marduwayh',
    'Usayd ibn Ḥuḍayr', 'As-Suddī', 'Abū Mālik', 'Abū Ṣāliḥ', 'Ibn ʿAbbās',
    'Murrah al-Hamadhānī', 'Abū ad-Dardāʾ', 'Mujāhid', 'Saʿīd ibn Jubayr', 'Nāfiʿ',
    'ʿAṭāʾ', 'Abū al-ʿĀliyah', 'ar-Rabīʿ ibn Anas', 'Muqātil ibn Ḥayān', 'Qatādah',
    'Ismāʿīl ibn Abī Khālid', 'Ibn Abī Ḥātim', 'Abū Jaʿfar ar-Rāzī', 'Abū Isḥāq',
    'Abū al-Aḥwaṣ', 'ʿAlī ibn Abī Ṭalḥah', 'Maʿmar', 'az-Zuhrī', 'Ibn Jarīr',
    'Qatādah ibn Diʿāmah', 'ʿAbdullāh ibn Masʿūd', 'Ibn Jurayj', 'ʿAbdullāh ibn Kathīr',
    'Al-Aʿmash', 'Ḥudhayfah', 'Kaʿb ibn al-Ashraf', 'Ḥuyayy ibn Akhṭab', 'Judayy ibn Akhṭab',
    'ʿUtbah ibn Rabīʿah', 'Shaybah ibn Rabīʿah', 'al-Walīd ibn al-Mughīrah',
    'Abū Jahl', 'Abū Lahab', 'Muḥammad ibn Isḥāq', 'al-Ḥasan', 'ʿAbdullāh ibn Salām',
    'ʿAbdullāh ibn Ubayy', 'Junayd of Baghdād', 'Jadd ibn Qays', 'Muʿaṭṭib ibn Qushayr',
    'ad-Daḥḥāk', 'Abū Burdah al-Aslamī', 'Ibn al-Sawdāʾ', 'ʿAbd al-Dār', 'ʿAwf ibn ʿĀmir',
    'Saʿīd ibn Jubayr', 'ʿAṭāʾ', 'al-Ḥasan al-Baṣrī', 'ʿAṭiyyah al-ʿAwfī', 'ʿAṭāʾ al-Khurāsānī',
    'Abū Mālik', 'Masrūq', 'Abū Jaʿfar ar-Rāzī', 'Abū Bakr', 'ʿUmar', 'Ādam',
    'ʿĀṣim ibn Kulayb', 'Saʿīd ibn Maʿbad', 'Anas ibn Mālik', 'al-Ashʿarī', 'Yūsuf',
    'Abū Dharr', 'Ibn Marduwyah', 'Muḥammad ibn Isḥāq', 'Ḥawwāʾ', 'Muḥammad ibn Kaʿb al-Quraẓī',
    'Khālid ibn Maʿdān', 'ʿAbd ar-Raḥmān ibn Zayd ibn Aslam', 'al-ʿAwfī', 'al-Ḥākim',
    'Abū Dāwūd aṭ-Ṭayālisī', 'Yaʿqūb', 'Muqātil', 'Abdur-Razzāq', 'Maʿmar',
    'Sulaymān ibn ʿAbd al-Malik', 'Abū Ḥāzim', 'ad-Dārimī', 'Muqātil ibn Ḥayān',
    'ʿUmar ibn al-Khaṭṭāb', 'Ismāʿīl ibn Abī Khālid', 'Muʿāwiyah ibn Ḥaydah al-Qushayrī',
    'Mūsā', 'ʿIkrimah', 'Qurayza', 'Naḍīr', 'ar-Rāghib al-Iṣfahānī', 'Namrūd',
    'al-Barāʾ ibn ʿĀzib', 'Abū Saʿīd al-Khudrī', 'Mukhairiq', 'Abul-ʿĀliyah',
    'Kaʿb ibn Ashraf', 'Ibn Khuwayz Mandadh', 'Rūmī', 'Abū ʿUthmān', 'Mazhari',
    'Thāna Bhawan', 'ʿĀʾisha'];
  const TITLES = ['Maʿārif-ul-Qurʾān', 'Tazkīrul Qurʾān', 'Al-Mukhtaṣar', 'Tanwīr al-Miqbās',
                  'Al-Jalālayn', 'Ibn Kathīr'];
  // fold diacritics/hamzas AND drop spaces, so "Ibn Masʿūd" matches the sources' "Ibn Mas'ud"
  const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[\u02bf\u02be\u02bc`'\u2019\u2018\-\s]/g, '').toLowerCase();

  // same person, different romanisation in the source corpus
  const VARIANTS = {
    'Ibn Marduwayh':       ['marduwyah', 'marduwayh'],
    'Murrah al-Hamadhānī': ['al-hamadani', 'alhamadhani'],
  };
  let checked = 0; const bad = [];
  for (let a = LO; a <= HI; a++) {
    const t = w.eval(`loadedGuidance[${S}].verses["${a}"].text`);
    // include sources for any verse in this surah that the prose explicitly cites
    const also = new Set([a]);
    for (const m of t.matchAll(new RegExp(`\\b${S}:(\\d+)\\b`, 'g'))) also.add(Number(m[1]));
    const blob = norm([...also].map(n =>
      w.eval(`getVerseCommentaryAll(loadedTafsir[${S}],${n}).map(e=>e.text).join(' ')`)).join(' '));
    for (const nm of NAMES) {
      if (!t.includes(nm)) continue;
      checked++;
      const parts = nm.normalize('NFD').replace(/[\u0300-\u036f]/g, '').split(/\s+/).filter(x => x.length > 3);
      const base = norm(parts[parts.length - 1] || nm);
      const ok = VARIANTS[nm] ? VARIANTS[nm].some(v => blob.includes(norm(v)))
                              : base.length > 2 && blob.includes(base);
      if (!ok) bad.push(`${S}:${a} "${nm}" (wanted "${base}")`);
    }
  }
  ck(`every named authority (${checked} checked) appears in that verse's sources`, bad.length === 0, bad.join('; '));

  const labels = norm(w.eval(`loadedTafsir[${S}].sources.map(s=>s.label).join(' | ')`));
  const badTitles = TITLES.filter(t => !labels.includes(norm(t).split(' ')[0]));
  ck('every tafsir title cited matches a real source label', badTitles.length === 0, badTitles.join('; '));

  // ---------- rendering ----------
  const html = w.eval(`renderCommentaryHtml(loadedTafsir[${S}], getVerseCommentary(loadedTafsir[${S}],${LO}), ${LO})`);
  const el = w.document.createElement('div'); el.innerHTML = html;
  ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
  ck('guidance range is its first line', el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
  ck(`range reads "${S}:${LO}"`, el.querySelector('.tafsir-guidance .tafsir-range').textContent.trim() === `${S}:${LO}`);
  const det = el.querySelector('details.tafsir-sources');
  ck('six sources folded behind a disclosure', !!det && det.querySelectorAll('.tafsir-entry').length === 6,
     det ? det.querySelectorAll('.tafsir-entry').length : 'none');

  // ---------- PARTIAL FILE: unauthorised verses must fall back ----------
  for (const a of [158, 159, 161, 286]) {
    const g = w.eval(`renderGuidanceHtml(loadedGuidance[${S}], ${a})`);
    ck(`${S}:${a} (not yet authored) yields no guidance`, g === '', JSON.stringify(g).slice(0, 60));
    const h = w.eval(`renderCommentaryHtml(loadedTafsir[${S}], getVerseCommentary(loadedTafsir[${S}],${a}), ${a})`);
    const e = w.document.createElement('div'); e.innerHTML = h;
    ck(`${S}:${a} falls back to six sources directly`, e.querySelectorAll('.tafsir-entry').length === 6,
       e.querySelectorAll('.tafsir-entry').length);
    ck(`${S}:${a} shows no disclosure`, !e.querySelector('details.tafsir-sources'));
    ck(`${S}:${a} first source marked primary`, e.querySelector('.tafsir-entry').classList.contains('tafsir-entry-primary'));
  }

  // ---------- modal ----------
  w.eval(`showExplanation(${S},3)`); await new Promise(r => setTimeout(r, 600));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal for 2:3 leads with guidance', body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
  ck('modal quotes the translation', body.includes('establish prayer'));

  // ---------- ebook: mixed authored / unauthorised ----------
  const ebook = await w.eval(`(async()=>{await loadChapterData(${S});
    AppState.currentSurah=${S};AppState.currentSurahData=loadedChapters[${S}];
    await Promise.all([loadTafsirData(${S}),loadGuidanceData(${S})]);
    const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  const gcount = (ebook.match(/data-source="guidance"/g) || []).length;
  ck(`ebook carries guidance on exactly the ${HI - LO + 1} authored verses`, gcount === HI - LO + 1, gcount);
  ck('ebook has no "coming soon"', !/coming soon/i.test(ebook));

  ck('no jsdom errors', errs.length === 0, errs.join(' | '));

  let pass = 0;
  for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
  console.log(`\n${pass}/${R.length} checks passed`);
  process.exit(pass === R.length ? 0 : 1);
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(2); });
