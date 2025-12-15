from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, List, Optional
import re
import json

class OlympicMatchAnalyzerInput(BaseModel):
    """Input schema for Olympic Match Analyzer Tool."""
    match_text: str = Field(..., description="The Olympic match text/description to analyze")

class OlympicMatchAnalyzer(BaseTool):
    """Tool for analyzing Olympic match texts and generating structured summaries."""

    name: str = "Olympic Match Analyzer"
    description: str = (
        "Analyzes Olympic match texts and generates structured summaries including "
        "team/athlete information, scores, key moments, and performance statistics. "
        "Supports both Spanish and English input and returns analysis in the same language."
    )
    args_schema: Type[BaseModel] = OlympicMatchAnalyzerInput

    def _detect_language(self, text: str) -> str:
        """Detect if text is in Spanish or English."""
        spanish_indicators = ['contra', 'partido', 'ganó', 'perdió', 'equipo', 'jugador', 'medalla', 'oro', 'plata', 'bronce', 'juegos', 'olímpicos']
        english_indicators = ['against', 'match', 'game', 'won', 'lost', 'team', 'player', 'medal', 'gold', 'silver', 'bronze', 'olympic', 'games']
        
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        return 'es' if spanish_count > english_count else 'en'

    def _is_olympic_content(self, text: str) -> bool:
        """Check if text is related to Olympic sports/events."""
        olympic_keywords = [
            'olympic', 'olympics', 'olímpico', 'olímpicos', 'juegos olímpicos',
            'olympic games', 'rio 2016', 'tokyo 2020', 'beijing 2022', 'paris 2024',
            'gold medal', 'silver medal', 'bronze medal', 'medalla de oro', 
            'medalla de plata', 'medalla de bronce', 'podium', 'podio'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in olympic_keywords)

    def _extract_teams_athletes(self, text: str) -> List[Dict[str, str]]:
        """Extract team/athlete names and countries."""
        participants = []
        
        # Pattern for "Team/Athlete (Country)" or "Country's Athlete"
        country_patterns = [
            r'([A-Z][a-zA-Z\s]+)\s*\(([A-Z]{2,3}|[A-Z][a-zA-Z\s]+)\)',
            r'([A-Z][a-zA-Z\s]+)\s*de\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s*from\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in country_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                participants.append({
                    'name': match[0].strip(),
                    'country': match[1].strip()
                })
        
        return participants

    def _extract_sport_event(self, text: str) -> Dict[str, Optional[str]]:
        """Extract sport and event type."""
        sports = [
            'swimming', 'athletics', 'gymnastics', 'basketball', 'football', 'soccer',
            'tennis', 'volleyball', 'boxing', 'wrestling', 'weightlifting', 'cycling',
            'natación', 'atletismo', 'gimnasia', 'baloncesto', 'fútbol', 'tenis',
            'voleibol', 'boxeo', 'lucha', 'halterofilia', 'ciclismo'
        ]
        
        text_lower = text.lower()
        sport_found = None
        
        for sport in sports:
            if sport in text_lower:
                sport_found = sport
                break
        
        # Extract event details (finals, semifinals, etc.)
        event_keywords = ['final', 'semifinal', 'quarter-final', 'preliminary', 'heat']
        event_found = None
        
        for event in event_keywords:
            if event in text_lower:
                event_found = event
                break
        
        return {'sport': sport_found, 'event': event_found}

    def _extract_scores_results(self, text: str) -> Dict[str, str]:
        """Extract scores and results."""
        results = {}
        
        # Score patterns
        score_patterns = [
            r'(\d+)-(\d+)',
            r'(\d+)\s*a\s*(\d+)',
            r'(\d+)\s*to\s*(\d+)'
        ]
        
        scores = []
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            scores.extend(matches)
        
        if scores:
            results['scores'] = [f"{s[0]}-{s[1]}" for s in scores]
        
        # Winner patterns
        winner_patterns = [
            r'won by ([A-Z][a-zA-Z\s]+)',
            r'ganó ([A-Z][a-zA-Z\s]+)',
            r'victory for ([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in winner_patterns:
            match = re.search(pattern, text)
            if match:
                results['winner'] = match.group(1).strip()
                break
        
        return results

    def _extract_key_moments(self, text: str) -> List[str]:
        """Extract key moments and highlights."""
        moment_indicators = [
            'turning point', 'crucial', 'decisive', 'highlight', 'spectacular',
            'punto decisivo', 'crucial', 'espectacular', 'momento clave'
        ]
        
        sentences = text.split('.')
        key_moments = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in moment_indicators):
                key_moments.append(sentence)
        
        return key_moments[:5]  # Limit to top 5 moments

    def _extract_statistics(self, text: str) -> Dict[str, str]:
        """Extract performance statistics."""
        stats = {}
        
        # Time patterns
        time_patterns = [
            r'(\d+:\d+\.\d+)',
            r'(\d+\.\d+)\s*seconds',
            r'(\d+\.\d+)\s*segundos'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                stats['time'] = match.group(1)
                break
        
        # Distance/height patterns
        distance_patterns = [
            r'(\d+\.\d+)\s*meters',
            r'(\d+\.\d+)\s*metros',
            r'(\d+\.\d+)m'
        ]
        
        for pattern in distance_patterns:
            match = re.search(pattern, text)
            if match:
                stats['distance'] = match.group(1) + 'm'
                break
        
        return stats

    def _generate_analysis(self, text: str, language: str) -> str:
        """Generate the structured analysis."""
        participants = self._extract_teams_athletes(text)
        sport_event = self._extract_sport_event(text)
        scores_results = self._extract_scores_results(text)
        key_moments = self._extract_key_moments(text)
        statistics = self._extract_statistics(text)
        
        if language == 'es':
            return self._generate_spanish_analysis(participants, sport_event, scores_results, key_moments, statistics, text)
        else:
            return self._generate_english_analysis(participants, sport_event, scores_results, key_moments, statistics, text)

    def _generate_english_analysis(self, participants, sport_event, scores_results, key_moments, statistics, text):
        """Generate analysis in English."""
        analysis = "# 🏅 Olympic Match Analysis\n\n"
        
        # Match Overview
        analysis += "## 📋 Match Overview\n"
        if sport_event['sport']:
            analysis += f"**Sport:** {sport_event['sport'].title()}\n"
        if sport_event['event']:
            analysis += f"**Event:** {sport_event['event'].title()}\n"
        
        if participants:
            analysis += "**Participants:**\n"
            for p in participants[:4]:  # Limit to 4 participants
                analysis += f"- {p['name']} ({p['country']})\n"
        analysis += "\n"
        
        # Final Result
        analysis += "## 🎯 Final Result\n"
        if 'scores' in scores_results:
            analysis += f"**Scores:** {', '.join(scores_results['scores'])}\n"
        if 'winner' in scores_results:
            analysis += f"**Winner:** {scores_results['winner']}\n"
        analysis += "\n"
        
        # Key Moments
        analysis += "## ⚡ Key Moments\n"
        if key_moments:
            for moment in key_moments:
                analysis += f"- {moment}\n"
        else:
            analysis += "- Key moments extracted from match context\n"
        analysis += "\n"
        
        # Performance Analysis
        analysis += "## 📊 Performance Analysis\n"
        analysis += "- Tactical and performance observations based on match description\n"
        if participants:
            analysis += f"- Outstanding performances by featured athletes\n"
        analysis += "\n"
        
        # Statistics
        analysis += "## 📈 Statistics\n"
        if statistics:
            for key, value in statistics.items():
                analysis += f"**{key.title()}:** {value}\n"
        else:
            analysis += "- Performance statistics as mentioned in match description\n"
        analysis += "\n"
        
        # Context & Significance
        analysis += "## 🌟 Context & Significance\n"
        analysis += "- Olympic implications and competitive context\n"
        if 'winner' in scores_results:
            analysis += "- Medal implications and championship impact\n"
        analysis += "- Historical significance within Olympic Games context\n"
        
        return analysis

    def _generate_spanish_analysis(self, participants, sport_event, scores_results, key_moments, statistics, text):
        """Generate analysis in Spanish."""
        analysis = "# 🏅 Análisis del Partido Olímpico\n\n"
        
        # Match Overview
        analysis += "## 📋 Resumen del Partido\n"
        if sport_event['sport']:
            analysis += f"**Deporte:** {sport_event['sport'].title()}\n"
        if sport_event['event']:
            analysis += f"**Evento:** {sport_event['event'].title()}\n"
        
        if participants:
            analysis += "**Participantes:**\n"
            for p in participants[:4]:  # Limit to 4 participants
                analysis += f"- {p['name']} ({p['country']})\n"
        analysis += "\n"
        
        # Final Result
        analysis += "## 🎯 Resultado Final\n"
        if 'scores' in scores_results:
            analysis += f"**Marcadores:** {', '.join(scores_results['scores'])}\n"
        if 'winner' in scores_results:
            analysis += f"**Ganador:** {scores_results['winner']}\n"
        analysis += "\n"
        
        # Key Moments
        analysis += "## ⚡ Momentos Clave\n"
        if key_moments:
            for moment in key_moments:
                analysis += f"- {moment}\n"
        else:
            analysis += "- Momentos clave extraídos del contexto del partido\n"
        analysis += "\n"
        
        # Performance Analysis
        analysis += "## 📊 Análisis de Rendimiento\n"
        analysis += "- Observaciones tácticas y de rendimiento basadas en la descripción del partido\n"
        if participants:
            analysis += f"- Actuaciones destacadas de los atletas principales\n"
        analysis += "\n"
        
        # Statistics
        analysis += "## 📈 Estadísticas\n"
        if statistics:
            for key, value in statistics.items():
                analysis += f"**{key.title()}:** {value}\n"
        else:
            analysis += "- Estadísticas de rendimiento mencionadas en la descripción del partido\n"
        analysis += "\n"
        
        # Context & Significance
        analysis += "## 🌟 Contexto y Significado\n"
        analysis += "- Implicaciones olímpicas y contexto competitivo\n"
        if 'winner' in scores_results:
            analysis += "- Implicaciones de medallas e impacto en el campeonato\n"
        analysis += "- Significado histórico dentro del contexto de los Juegos Olímpicos\n"
        
        return analysis

    def _run(self, match_text: str) -> str:
        """Analyze Olympic match text and return structured summary."""
        try:
            # Validate input
            if not match_text or not match_text.strip():
                return "Error: Please provide a valid match text for analysis."
            
            # Check if content is Olympic-related
            if not self._is_olympic_content(match_text):
                language = self._detect_language(match_text)
                if language == 'es':
                    return "❌ Error: Esta herramienta está diseñada específicamente para el análisis de partidos olímpicos. El texto proporcionado no parece estar relacionado con eventos olímpicos. Por favor, proporcione una descripción de un partido o evento olímpico."
                else:
                    return "❌ Error: This tool is specifically designed for Olympic match analysis. The provided text does not appear to be related to Olympic events. Please provide a description of an Olympic match or event."
            
            # Detect language
            language = self._detect_language(match_text)
            
            # Generate analysis
            analysis = self._generate_analysis(match_text, language)
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing match text: {str(e)}. Please ensure you provided a valid Olympic match description."