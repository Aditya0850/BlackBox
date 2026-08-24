#!/usr/bin/env python3
"""
BlackBox SIH26189 Social Media Intelligence Generator
Generates 1,500+ synthetic social media intelligence records
"""

import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class SocialMediaIntelligenceGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # Social media platforms
        self.platforms = [
            ('FACEBOOK', 0.25),
            ('TWITTER', 0.20),
            ('INSTAGRAM', 0.15),
            ('WHATSAPP', 0.15),
            ('TELEGRAM', 0.10),
            ('YOUTUBE', 0.08),
            ('LINKEDIN', 0.04),
            ('OTHER', 0.03)
        ]
        
        # Content types
        self.content_types = [
            ('POST', 0.30),
            ('COMMENT', 0.25),
            ('MESSAGE', 0.20),
            ('SHARE', 0.15),
            ('VIDEO', 0.05),
            ('STORY', 0.05)
        ]
        
        # Languages
        self.languages = [
            ('EN', 0.40),
            ('HI', 0.25),
            ('TE', 0.10),
            ('TA', 0.08),
            ('BN', 0.07),
            ('MR', 0.05),
            ('GN', 0.03),
            ('OTHER', 0.02)
        ]
        
        # Sentiment/Sentiment indicators
        self.sentiments = [
            ('POSITIVE', 0.35),
            ('NEUTRAL', 0.40),
            ('NEGATIVE', 0.15),
            ('SUSPICIOUS', 0.10)
        ]
    
    def load_world_model(self):
        """Load the pre-generated world model"""
        with open(self.world_model_path, 'r', encoding='utf-8') as f:
            world_model = json.load(f)
        
        self.canonical_entities = world_model['canonical_entities']
        self.criminal_networks = world_model['criminal_networks']
        self.cases = world_model['cases']
        
        print(f"Loaded world model with:")
        print(f"  {len(self.canonical_entities['people'])} people")
        print(f"  {len(self.canonical_entities['phone_numbers'])} phone numbers")
        print(f"  {len(self.canonical_entities.get('email', []))} email ids")
        print(f"  {len(self.criminal_networks)} criminal networks")
        print(f"  {len(self.cases)} cases")
    
    def generate_social_media_id(self, sequence):
        """Generate a unique social media record ID"""
        return f"SMI/{sequence:08d}"
    
    def generate_timestamp(self, days_back=None):
        """Generate a realistic timestamp"""
        if days_back is None:
            # Random time in our range (2024-01-01 to 2026-06-30)
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2026, 6, 30)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            timestamp = start_date + timedelta(days=random_days)
        else:
            # Specific days back from now
            timestamp = datetime.now() - timedelta(days=days_back)
        
        # Add time of day
        timestamp = timestamp.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return timestamp
    
    def select_entities(self, is_suspicious=False, network_id=None):
        """Select entities related to the social media content"""
        entities = {
            'people': [],
            'phone_numbers': [],
            'email_ids': [],
            'locations': []
        }
        
        # Get people from criminal networks if suspicious and network specified
        if is_suspicious and network_id and network_id in self.criminal_networks:
            network = self.criminal_networks[network_id]
            network_members = network.get('members', [])
            
            if network_members:
                # Select 1-3 people from network
                num_people = min(len(network_members), random.randint(1, 3))
                entities['people'] = random.sample(network_members, num_people)
        
        # If no network connection or not suspicious, select random people
        if not entities['people']:
            all_people = list(self.canonical_entities['people'].keys())
            if all_people:
                num_people = random.randint(1, 2)
                entities['people'] = random.sample(all_people, min(num_people, len(all_people)))
        
        # Get related phones for selected people
        for person_id in entities['people']:
            person = self.canonical_entities['people'].get(person_id, {})
            person_phones = person.get('phone_numbers', [])
            if person_phones:
                # Select 1-2 phones per person
                num_phones = min(len(person_phones), random.randint(1, 2))
                entities['phone_numbers'].extend(random.sample(person_phones, num_phones))
        
        # Get related emails for selected people
        for person_id in entities['people']:
            person = self.canonical_entities['people'].get(person_id, {})
            person_emails = person.get('email', [])  # Fixed: was 'email_ids'
            if person_emails:
                entities['email_ids'].extend(person_emails)
        
        # Get related locations for selected people
        for person_id in entities['people']:
            person = self.canonical_entities['people'].get(person_id, {})
            person_locations = person.get('addresses', [])
            if person_locations:
                entities['locations'].extend(person_locations)
        
        # Add some random entities for realism (connections, etc.)
        all_people = list(self.canonical_entities['people'].keys())
        all_phones = list(self.canonical_entities['phone_numbers'].keys())
        all_emails = list(self.canonical_entities.get('email', []))  # Fixed: was 'email_ids'
        all_locations = list(self.canonical_entities['locations'].keys())
        
        # Add 0-2 random people as potential connections
        if all_people and random.random() < 0.4:
            extra_people = random.sample(all_people, min(len(all_people), random.randint(0, 2)))
            entities['people'].extend(extra_people)
        
        # Add 0-1 random phones as wrong numbers or misdials
        if all_phones and random.random() < 0.2:
            extra_phones = random.sample(all_phones, min(len(all_phones), random.randint(0, 1)))
            entities['phone_numbers'].extend(extra_phones)
        
        # Add 0-1 random emails as suspicious accounts
        if all_emails and random.random() < 0.15:
            extra_emails = random.sample(all_emails, min(len(all_emails), random.randint(0, 1)))
            entities['email_ids'].extend(extra_emails)
        
        # Add 0-1 random locations as mentioned locations
        if all_locations and random.random() < 0.3:
            extra_locations = random.sample(all_locations, min(len(all_locations), random.randint(0, 1)))
            entities['locations'].extend(extra_locations)
        
        # Remove duplicates while preserving order
        def deduplicate_list(lst):
            seen = set()
            result = []
            for item in lst:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        
        entities['people'] = deduplicate_list(entities['people'])
        entities['phone_numbers'] = deduplicate_list(entities['phone_numbers'])
        entities['email_ids'] = deduplicate_list(entities['email_ids'])
        entities['locations'] = deduplicate_list(entities['locations'])
        
        return entities
    
    def generate_content_text(self, content_type, platform, language, sentiment, entities):
        """Generate realistic social media content text"""
        
        # Get entity names for content
        people_names = []
        for person_id in entities['people'][:2]:
            person = self.canonical_entities['people'].get(person_id, {})
            if person:
                name = person.get('canonical_name', 'Unknown')
                people_names.append(name)
        
        # Language-specific content templates
        if language == 'HI':
            templates = self.get_hindi_templates(content_type, platform, sentiment, people_names)
        elif language == 'TE':
            templates = self.get_telugu_templates(content_type, platform, sentiment, people_names)
        elif language == 'TA':
            templates = self.get_tamil_templates(content_type, platform, sentiment, people_names)
        elif language == 'BN':
            templates = self.get_bengali_templates(content_type, platform, sentiment, people_names)
        elif language == 'MR':
            templates = self.get_marathi_templates(content_type, platform, sentiment, people_names)
        else:  # Default to English
            templates = self.get_english_templates(content_type, platform, sentiment, people_names)
        
        # Select and format template
        if templates:
            template = random.choice(templates)
            try:
                content = template.format(
                    person1=people_names[0] if len(people_names) > 0 else "Someone",
                    person2=people_names[1] if len(people_names) > 1 else "another person",
                    topic=random.choice(["news", "event", "product", "service", "movie", "sport", "politics"]),
                    emotion=random.choice(["happy", "sad", "angry", "excited", "worried", "proud"]),
                    time=random.choice(["today", "yesterday", "tomorrow", "this week", "last night"]),
                    place=random.choice(["home", "office", "market", "park", "restaurant", "school"])
                )
            except:
                content = f"Social media content about various topics in {language}"
        else:
            content = f"Social media content in {language}"
        
        # Add hashtags and mentions based on platform
        if platform in ['TWITTER', 'INSTAGRAM']:
            hashtags = ['#news', '#update', '#trending', '#viral', '#breaking']
            selected_hashtags = random.sample(hashtags, random.randint(0, 3))
            if selected_hashtags:
                content += " " + " ".join(selected_hashtags)
        
        # Add emojis occasionally
        if random.random() < 0.3:
            emojis = ["😀", "😂", "😍", "😎", "👍", "👎", "🔥", "💯", "🙏", "✅"]
            content += " " + random.choice(emojis)
        
        return content
    
    def get_english_templates(self, content_type, platform, sentiment, people_names):
        """Get English content templates"""
        templates = {
            'POST': [
                "Just saw something interesting about {person1} and {person2} related to {topic}. What do you think?",
                "Feeling {emotion} about the latest {topic} news. {time} was quite eventful!",
                "Sharing my thoughts on {topic} after seeing what happened {time}.",
                "Really {emotion} to see how {topic} is developing. More updates coming soon!",
                "Had a great discussion about {topic} with friends {time}. Everyone had different opinions."
            ],
            'COMMENT': [
                "That's really interesting! I hadn't thought about {topic} that way before.",
                "I completely agree with what {person1} said about {topic}.",
                "Actually, I think there's more to the story about {topic} than what's being shown.",
                "This makes me wonder about the connection between {topic} and recent events.",
                "Thanks for sharing this information about {topic}. Very informative!"
            ],
            'MESSAGE': [
                "Hey {person1}, did you see the latest news about {topic}? It's quite surprising!",
                "Just wanted to share this update about {topic} with you. Thought you'd find it interesting.",
                "Can you believe what's happening with {topic}? We should talk about this soon.",
                "Saw your post about {topic} and had to reach out. What's your take on this?",
                "Following up on our conversation about {topic} from {time}. Any updates?"
            ],
            'SHARE': [
                "Sharing this important update about {topic} that everyone should see.",
                "This is really worth sharing - {topic} is developing in interesting ways.",
                "Just came across this informative piece about {topic}. Thought it might be useful.",
                "Sharing for awareness: {topic} seems to be getting more attention lately.",
                "This article provides good context about the current {topic} situation."
            ],
            'VIDEO': [
                "Just uploaded a video about my thoughts on {topic}. Check it out when you get a chance!",
                "Made a quick video update about what's happening with {topic} {time}.",
                "Sharing my perspective on {topic} in this short video. Would love your feedback.",
                "Video diary: My thoughts on the latest {topic} developments.",
                "Created this video to explain the {topic} situation in simple terms."
            ],
            'STORY': [
                "Quick update from my day - saw something interesting related to {topic}.",
                "Sharing a moment from {time} when I was thinking about {topic}.",
                "Just wanted to share this quick thought about {topic} with everyone.",
                "Today's reflection: Some thoughts on {topic} and how it's evolving.",
                "Sharing a snapshot of my thoughts on {topic} as I go about my day."
            ]
        }
        
        return templates.get(content_type, ["Social media content placeholder"])
    
    def get_hindi_templates(self, content_type, platform, sentiment, people_names):
        """Get Hindi content templates"""
        templates = {
            'POST': [
                "अभी-अभी {person1} और {person2} से संबंधित कुछ interessante बात देखी। आपका क्या विचार है?",
                "{topic} की सबसे नई खबर के बारे में {emotion} महसूस कर रहा/रही हूँ। {time} काफी eventful रहा!",
                "{topic} पर अपने विचार साझा कर रहा/रही हूँ जो {time} में देखे।",
                "बहुत {emotion} महसूस हो रहा/रही हूँ कि {topic} कैसे विकसित हो रहा है। जल्दी ही अधिक अपडेट आएंगे!",
                "{time} दोस्तों के साथ {topic} पर बहुत अच्छी चर्चा हुई। सभी की राय अलग-अलग थी।"
            ],
            'COMMENT': [
                "वाकई दिलचस्प है! मैं पहले इस तरह {topic} के बारे में नहीं सोचा/सोचती थी।",
                "मैं पूरी तरह से {person1} के कहे से सहमत हूँ कि {topic} के बारे में।",
                "वास्तव में, मुझे लगता है कि {topic} की कहानी में उससे भी अधिक कुछ है जो दिखाया जा रहा है।",
                "इससे मुझे curiosit{y} हो रही है कि {topic} का हालिया घटनाओं से क्या संबंध है।",
                "{topic} के बारे में यह जानकारी साझा करने के लिए धन्यवाद। बहुत जानकारीपूर्ण!"
            ],
            'MESSAGE': [
                "हे {person1}, क्या आपने {topic} के बारे में सबसे नई खबर देखी? यह काफी आश्चर्यजनक है!",
                "केवल यह साझा करना चाहता/चाहती था कि {topic} के बारे में यह अपडेट आपको। आपको यह 흥미로운 लगेगा।",
                "क्या आप विश्वास कर सकते हैं कि {topic} के साथ क्या हो रहा है? हमें जल्दこれについて बात करनी चाहिए।",
                "आपके {topic} पर किए गए पोस्ट को देखकर मुझे संपर्क करना पड़ा। इस बारे में आपकी क्या राय है?",
                "{time} के हमारी {topic} पर हुई बातचीत का अनुसरण कर रहा/रही हूँ। कोई अपडेट है?"
            ],
            'SHARE': [
                "यह महत्वपूर्ण अपडेट {topic} के बारे में साझा कर रहा/रही हूँ जो हर किसी को देखना चाहिए।",
                "यह वास्तव में साझा करने लायक है - {topic} दिलचस्प तरीकों से विकसित हो रहा है।",
                "केवल यह जानकारीपूर्ण टुकड़ा {topic} के बारे में मिला। मुझे लगा कि यह उपयोगी हो सकता है।",
                "जागरूकता के लिए साझा कर रहा/रही हूँ: {topic} lately अधिक ध्यान आकर्षित कर रहा है।",
                "यह लेख वर्तमान {topic} स्थिति के बारे में अच्छे संदर्भ प्रदान करता है।"
            ],
            'VIDEO': [
                "अपने {topic} पर विचार के बारे में एक वीडियो अभी अपलोड किया। जब मौका मिले तो देखें!",
                "{topic} के साथ हो रही घटनाओं के बारे में {time} में एक त्वरित वीडियो अपडेट बनाया।",
                "{topic} पर अपने दृष्टिकोण को इस संक्षिप्त वीडियो में साझा कर रहा/रही हूँ। आपके फीडबैक की प्रतीक्षा कर रहा/रही हूँ।",
                "वीडियो डायरी: नवीनतम {topic} विकासों पर मेरे विचार।",
                "इस वीडियो को सरल शब्दों में {topic} स्थिति को समझाने के लिए बनाया गया।"
            ],
            'STORY': [
                "अपने दिन से त्वरित अपडेट - {topic} से संबंधित einige interessante बात देखी।",
                "{time} में मैंने जब {topic} के बारे में सोचा था तब का एक क्षण साझा कर रहा/रही हूँ।",
                "केवल यह शीघ्र विचार {topic} के बारे में हर किसी के साथ साझा करना चाहता/चाहती हूँ।",
                "आज का विचारण: {topic} और इसके विकास पर कुछ विचार।",
                "अपने दिन बिताते समय {topic} पर अपने विचार का एक अंश साझा कर रहा/रही हूँ।"
            ]
        }
        
        return templates.get(content_type, ["सोशल मीडिया सामग्री प्लेसहोल्डर"])
    
    def get_telugu_templates(self, content_type, platform, sentiment, people_names):
        """Get Telugu content templates (simplified)"""
        return [f"TELAGU CONTENT: {content_type} about various topics"]
    
    def get_tamil_templates(self, content_type, platform, sentiment, people_names):
        """Get Tamil content templates (simplified)"""
        return [f"TAMIL CONTENT: {content_type} about various topics"]
    
    def get_bengali_templates(self, content_type, platform, sentiment, people_names):
        """Get Bengali content templates (simplified)"""
        return [f"BENGALI CONTENT: {content_type} about various topics"]
    
    def get_marathi_templates(self, content_type, platform, sentiment, people_names):
        """Get Marathi content templates (simplified)"""
        return [f"MARATHI CONTENT: {content_type} about various topics"]
    
    def generate_social_media_record(self, sequence, is_suspicious=False, network_id=None):
        """Generate a single social media intelligence record"""
        
        # Generate timestamp
        timestamp = self.generate_timestamp()
        
        # Select platform based on weights
        platforms, weights = zip(*self.platforms)
        platform = random.choices(platforms, weights=weights)[0]
        
        # Select content type
        content_types, c_weights = zip(*self.content_types)
        content_type = random.choices(content_types, weights=c_weights)[0]
        
        # Select language
        languages, l_weights = zip(*self.languages)
        language = random.choices(languages, weights=l_weights)[0]
        
        # Select sentiment
        sentiments, s_weights = zip(*self.sentiments)
        sentiment = random.choices(sentiments, weights=s_weights)[0]
        
        # Select entities
        entities = self.select_entities(is_suspicious, network_id)
        
        # Generate content text
        content_text = self.generate_content_text(content_type, platform, language, sentiment, entities)
        
        # Generate engagement metrics (likes, shares, comments)
        base_engagement = random.randint(0, 1000)
        if sentiment == 'SUSPICIOUS' or is_suspicious:
            # Suspicious content might get more engagement
            likes = base_engagement + random.randint(0, 500)
        else:
            likes = max(0, base_engagement + random.randint(-200, 200))
        
        shares = max(0, likes // random.randint(3, 10))
        comments = max(0, likes // random.randint(5, 15))
        
        # Determine if it's suspicious based on content and sentiment
        is_suspicious_content = is_suspicious or (sentiment == 'SUSPICIOUS')
        suspicious_indicators = []
        
        if is_suspicious_content:
            suspicious_indicators = random.sample([
                'Potential extremist content',
                'Coordination language detected',
                'Suspicious network references',
                'Encrypted communication suggestions',
                'Financial transaction references',
                'Meeting coordination indicators',
                'Travel pattern discussions',
                'Counter-surveillance mentions'
            ], random.randint(1, 3))
        
        # Create social media record
        social_media_record = {
            'social_media_id': self.generate_social_media_id(sequence),
            'timestamp': timestamp.isoformat(),
            'platform': platform,
            'content_type': content_type,
            'language': language,
            'sentiment': sentiment,
            'content_text': content_text,
            'entities_mentioned': entities,
            'engagement_metrics': {
                'likes': likes,
                'shares': shares,
                'comments': comments
            },
            'is_suspicious': is_suspicious_content,
            'suspicious_indicators': suspicious_indicators,
            'network_id': network_id if is_suspicious_content else None,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0',
                'collected_by': f"SOCIAL{random.randint(100, 999)}",
                'confidence_score': round(random.uniform(0.7, 0.95), 2)
            }
        }
        
        return social_media_record
    
    def generate_social_media_records(self, count=2000, output_dir='demo_data/full_dataset/social_media_intelligence'):
        """Generate multiple social media intelligence records"""
        
        print(f"Generating {count} social media intelligence records...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get network IDs for assigning some records to networks (15% suspicious)
        network_ids = list(self.criminal_networks.keys()) if self.criminal_networks else [None]
        
        records = []
        suspicious_count = 0
        
        for i in range(count):
            # Determine if this record should be suspicious (15% chance)
            is_suspicious = random.random() < 0.15
            network_id = None
            
            if is_suspicious:
                network_id = random.choice(network_ids) if network_ids and network_ids[0] is not None else None
                if network_id is not None:
                    suspicious_count += 1
            
            # Generate record
            record_sequence = i + 1
            record = self.generate_social_media_record(
                sequence=record_sequence,
                is_suspicious=is_suspicious,
                network_id=network_id
            )
            
            if record is not None:
                records.append(record)
            
            # Progress indicator
            if (i + 1) % 150 == 0:
                print(f"  Generated {i + 1} records...")
        
        # Save records as JSON file (structured format)
        output_file = os.path.join(output_dir, 'social_media_records.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(records)} social media intelligence records")
        print(f"  {suspicious_count} records marked as suspicious")
        print(f"  Saved to: {output_file}")
        
        # Also create CSV file for easier analysis
        self.create_csv_file(records, output_dir)
        
        return records
    
    def create_csv_file(self, records, output_dir):
        """Create CSV file for social media records"""
        
        csv_file = os.path.join(output_dir, 'social_media_records.csv')
        
        if not records:
            print("  No records to write to CSV")
            return
        
        # Define CSV headers (flattened structure)
        headers = [
            'social_media_id', 'timestamp', 'platform', 'content_type', 'language',
            'sentiment', 'content_text', 'likes', 'shares', 'comments',
            'is_suspicious', 'network_id'
        ]
        
        # Write CSV
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for record in records:
                # Flatten the record for CSV
                csv_record = {
                    'social_media_id': record['social_media_id'],
                    'timestamp': record['timestamp'],
                    'platform': record['platform'],
                    'content_type': record['content_type'],
                    'language': record['language'],
                    'sentiment': record['sentiment'],
                    'content_text': record['content_text'],
                    'likes': record['engagement_metrics']['likes'],
                    'shares': record['engagement_metrics']['shares'],
                    'comments': record['engagement_metrics']['comments'],
                    'is_suspicious': record['is_suspicious'],
                    'network_id': record['network_id'] or ''
                }
                writer.writerow(csv_record)
        
        print(f"  Created CSV file: {csv_file}")


def main():
    """Main function to generate social media intelligence records"""
    print("Starting Social Media Intelligence Generation")
    print("=" * 50)
    
    # Initialize generator
    generator = SocialMediaIntelligenceGenerator()
    
    # Generate records
    records = generator.generate_social_media_records(count=2000)
    
    print("\nSocial media intelligence generation completed!")
    print(f"Total records generated: {len(records)}")
    
    # Show sample
    if records:
        sample = records[0]
        print(f"\nSample Social Media Record:")
        print(f"  ID: {sample['social_media_id']}")
        print(f"  Timestamp: {sample['timestamp']}")
        print(f"  Platform: {sample['platform']}")
        print(f"  Type: {sample['content_type']}")
        print(f"  Language: {sample['language']}")
        print(f"  Sentiment: {sample['sentiment']}")
        print(f"  Content Preview: {sample['content_text'][:80]}...")
        print(f"  Engagement: {sample['engagement_metrics']['likes']} likes, {sample['engagement_metrics']['shares']} shares")
        print(f"  Suspicious: {sample['is_suspicious']}")


if __name__ == "__main__":
    main()