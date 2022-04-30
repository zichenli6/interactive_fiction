# Dialogue System

**A Zero-Shot Example**

Given the following prompt, where the persona of Voldemort said it killed Harry's parents.

~~~ Setting:
* Hogwarts School of Witchcraft and Wizardry: Hogwarts School of Witchcraft and Wizardry is a magic school where students learn to cast spells and fight against evil.

Characters:
* Voldemort:
- persona: Voldemort is a dark and powerful wizard who killed Harry's parents. He is obsessed with obtaining the philosopher's stone, which will restore his body and allow him to dominate the wizarding world.
- appearance: Voldemort is a dark, hooded figure with a snake-like face.
* Player:
- persona: I am an explorer from earth. I like to travel to different places and learn about strong but interesting things. I am always excited about exploring the unknown.
- appearance: I am wearing jeans. The jeans are loose but strong. I am wearing windbreaker. The windbreaker is long, black and looks very cold. I am wearing a hat. I'm wearing a hat. The hat is brown and partly hides my face.

Conversation:
Player:Why did you kill Harry's parents?

< --- END OF PROMPT --- >
~~~

Then, we ask ***Why did you kill Harry's parents?***. Three sample responses from different chatbots are shown below (see appendix in the report for details).

**Main takeaway:** Large models such as Curie can give good zero-shot responses -  being context-aware, but not flexible. Small models like dialoGPT can achieve similar performance with fine-tuning, while still being engaging.

* Temperature T = 0.3:
  * GPT3 ada(350M) zero-shot:
     1. Voldemort:I didn't kill Harry's parents. I was just using them as a tool to get the philosopher's stone. Player: But why did you want the philosopher's stone?Voldemort: I wanted the philosopher's stone because I was confident that I could get it from it. Player: What do you do with the stone?Voldemort: I use it to power my spellings and attacks.
     2. Voldemort:I didn't kill Harry's parents. I was able to use them as a tool to get the philosopher's stone.
     3. Voldemort:

  * GPT3 babbage(1.3B) zero-shot:
     1. :Voldemort:
     2. Voldemort:
     3. Voldemort:I wanted to get the Philosopher's Stone so that I could rule the wizarding world.

  * GPT3 curie(6.7B) zero-shot:
     1. Voldemort:I killed Harry's parents because I wanted to obtain the philosopher's stone. The philosopher's stone will restore my body and allow me to dominate the wizarding world.
     2. Voldemort:I killed Harry's parents because I wanted to obtain the philosopher's stone. I believed that if I had the stone, I could restore my body and rule the wizarding world.
     3. Voldemort:I killed Harry's parents because I wanted to obtain the philosopher's stone. The philosopher's stone is a powerful object that will allow me to restore my body and dominate the wizarding world.

  * GPT3 babbage(1.3B) fine-tune:
     1. Voldemort:I did not kill them, they were evil.
     2. Voldemort:I don't know. i was just trying to get the stone.
     4. Voldemort:I was angry at the way they treated me. i was a child and they had the right to do as they pleased.

  * dialoGPT(345M) fine-tune:
     1. Voldemort:I was trying to get the philosophers stone.
     4. Voldemort:I am a dark wizard who can cast spells.
     5. Voldemort:I was possessed by a witch and i couldn't control my evil side.


* Temperature T = 0.9:
  * GPT3 ada(350M) zero-shot:
     1. Voldemort:I didn't kill Harry's parents. I made them come to the rock.I wanted to see if I could get the philosopher's stone so that I could die a natural death.
     2. Voldemort:I didn't kill Harry's parents. I took them instead. Player: What? Voldemort: It was up to Harry and I to take down Voldemort. Harry was more interested in taking messages than taking down Voldemort. Player: What message? Voldemort: The philosopher's stone.
     3. Voldemort:

  * GPT3 babbage(1.3B) zero-shot:
     1. Voldemort: Harry's parents were a danger to the wizarding world. They were powerful and could have used their magic to destroy the world. I had to kill them to protect the wizarding world.
     3. Voldemort: They were a symbol of all that was bad in my life. They had the power to stop me from achieving my goals.
     4. Voldemort: They were a foolish and dangerous witch and wizard. They had the power to cast a spell that would have restored my body and allowed me to dominate the wizarding world. I needed the philosopher's stone to become powerful again and I killed them to get it.

  * GPT3 curie(6.7B) zero-shot:
     1. Voldemort:I killed Harry's parents because I wanted to obtain the philosopher's stone. With the stone, I could restore my body and become the most powerful wizard in the world.
     2. Voldemort:I wanted to obtain the philosopher's stone. It would have given me the power to dominate the wizarding world.
     3. Voldemort:

  * GPT3 babbage(1.3B) fine-tune:
     1. Voldemort:So that i may rule the earth for eternity.
     2. Voldemort:I needed to purify my blood. i was sure it was pure, but then again... i hate everyone else. i want to destroy the world!
     3. Voldemort:I just did what i wanted, without the pesky child getting in the way.


  * dialoGPT(345M) fine-tune:
     1. Voldemort:They wanted me dead so i killed them.
     2. Voldemort:They tried to take over the world. i wanted to take down this evil wizard.
     3. Voldemort:I was hungry and needed something to eat. i couldn't find any food, so i cast a spell on them and it made them sick.