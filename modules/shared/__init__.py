# modules/shared
from modules.shared.file_manager import file_mgr, FileManager
from modules.shared.gemini_service import gemini_service, GeminiService
from modules.shared.openai_service import openai_service, OpenAIService
from modules.shared.chart_generator import chart_generator, ChartGenerator
from modules.shared.docx_styler import DocxStyler
from modules.shared.obscura_harvester import obscura_harvester, ObscuraHarvester
from modules.shared.academic_enricher import academic_enricher, AcademicEnricher
from modules.shared.looped_flows_engine import looped_flows_engine, LoopedFlowController, LoopedFlowsReasoningService
from modules.shared.data_autocleaning import scientific_data_cleaner, ScientificDataCleaner
from modules.shared.reactome_service import reactome_service, ReactomeService
from modules.shared.academic_fact_checker import academic_fact_checker, AcademicFactChecker
from modules.shared.pubchem_service import pubchem_service, PubChemService
