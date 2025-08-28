#!/usr/bin/env python3
"""
Parallel Yahoo Finance Scraping with Database Storage
Uses multiprocessing to scrape multiple tickers simultaneously
"""

import os
from dotenv import load_dotenv
import multiprocessing as mp
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

# Load environment variables from .env file
load_dotenv()

# Global constants (initial defaults)
BATCH_SIZE = 10
NUM_PROCESSES = 6
TICKER_FILE = 'all_tickers.txt'
RESULTS_DIR = 'parallel_results'
ONLY_MISSING = False
USE_SCRAPINGBEE = False

# Logging config
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
)


def load_tickers(limit: int | None = None, ticker_list: str | None = None) -> List[str]:
	"""
	Load tickers from file or from provided comma-separated list
	
	Args:
		limit: Maximum number of tickers to load
		ticker_list: Comma-separated string of tickers (overrides file)
		
	Returns:
		List of ticker symbols
	"""
	if ticker_list:
		# Use provided ticker list
		tickers = [t.strip().upper() for t in ticker_list.split(',') if t.strip()]
		logging.info(f'Loaded {len(tickers)} tickers from command line: {tickers[:5]}{"..." if len(tickers) > 5 else ""}')
	else:
		# Load from file
		with open(TICKER_FILE, 'r') as f:
			tickers = [line.strip() for line in f if line.strip()]
		logging.info(f'Loaded {len(tickers)} tickers from file: {TICKER_FILE}')
	
	return tickers[:limit] if limit else tickers


def chunk(lst: List[str], size: int) -> List[List[str]]:
	return [lst[i:i + size] for i in range(0, len(lst), size)]


def process_worker(worker_id: int, batches: List[List[str]], batch_size: int, use_scrapingbee: bool) -> dict:
	start_time = time.time()
	logger = logging.getLogger(f'worker-{worker_id}')
	logger.info(f'Starting worker with {len(batches)} batches (batch_size={batch_size})')

	scraper = YahooFinanceAPIScraper(use_scrapingbee=use_scrapingbee)
	db = DatabaseManager()

	total_saved = 0
	total_fetched = 0
	failed_batches = 0

	for idx, tick_batch in enumerate(batches, start=1):
		try:
			logger.info(f'Worker {worker_id}: fetching batch {idx}/{len(batches)}: {tick_batch}')
			data = scraper.get_batch_tickers_info(tick_batch, batch_size=batch_size)
			total_fetched += len(data)

			if not data:
				failed_batches += 1
				continue

			logger.info(f'Worker {worker_id}: saving {len(data)} records to DB')
			if db.save_batch_ticker_data(data):
				total_saved += len(data)
			else:
				failed_batches += 1
		except Exception as e:
			failed_batches += 1
			logger.error(f'Worker {worker_id}: error on batch {idx}: {e}')

	# finalize
	db.close_connection()
	duration = time.time() - start_time
	result = {
		'worker_id': worker_id,
		'batches': len(batches),
		'total_fetched': total_fetched,
		'total_saved': total_saved,
		'failed_batches': failed_batches,
		'duration_sec': round(duration, 2)
	}
	return result


def distribute_batches(all_batches: List[List[str]], num_workers: int) -> List[List[List[str]]]:
	# Round-robin distribute batches among workers for balance
	workers: List[List[List[str]]] = [[] for _ in range(num_workers)]
	for i, b in enumerate(all_batches):
		workers[i % num_workers].append(b)
	return workers


def main(limit: int | None = None, ticker_list: str | None = None):
	os.makedirs(RESULTS_DIR, exist_ok=True)

	# Load tickers (load all if only-missing requested)
	if ONLY_MISSING:
		tickers = load_tickers(limit=None, ticker_list=ticker_list)
	else:
		tickers = load_tickers(limit=limit, ticker_list=ticker_list)
	if not tickers:
		logging.error('No tickers loaded')
		return 1

	# If only-missing, filter out tickers already up-to-date (today)
	if ONLY_MISSING:
		logging.info('only-missing enabled: filtering tickers that already have data today')
		db_check = DatabaseManager()
		if db_check.fallback_mode:
			logging.warning('Database in fallback mode; cannot filter missing. Proceeding with all tickers.')
		else:
			up_to_date = db_check.get_tickers_with_data_today(tickers)
			before = len(tickers)
			tickers = [t for t in tickers if t not in up_to_date]
			db_check.close_connection()
			logging.info(f'Filtered {before - len(tickers)} up-to-date tickers; {len(tickers)} remaining')
		if not tickers:
			logging.info('No missing tickers to process. Exiting.')
			return 0

	# Build batches of configured size
	all_batches = chunk(tickers, BATCH_SIZE)
	num_batches = len(all_batches)
	logging.info(f'Loaded {len(tickers)} tickers as {num_batches} batches of {BATCH_SIZE}')

	# Distribute to workers
	assigned = distribute_batches(all_batches, NUM_PROCESSES)
	for wid, batches in enumerate(assigned):
		logging.info(f'Worker {wid}: {len(batches)} batches')

	start = time.time()
	ctx = mp.get_context('spawn')
	with ctx.Pool(processes=NUM_PROCESSES) as pool:
		results = pool.starmap(process_worker, [(i, assigned[i], BATCH_SIZE, USE_SCRAPINGBEE) for i in range(NUM_PROCESSES)])

	total_saved = sum(r['total_saved'] for r in results)
	total_fetched = sum(r['total_fetched'] for r in results)
	total_failed = sum(r['failed_batches'] for r in results)
	dur = round(time.time() - start, 2)

	summary = {
		'timestamp': datetime.now().isoformat(),
		'num_processes': NUM_PROCESSES,
		'batch_size': BATCH_SIZE,
		'tickers': len(tickers),
		'batches': num_batches,
		'total_fetched': total_fetched,
		'total_saved': total_saved,
		'failed_batches': total_failed,
		'duration_sec': dur,
		'per_worker': results,
	}

	out_file = os.path.join(RESULTS_DIR, f'parallel_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
	with open(out_file, 'w') as f:
		json.dump(summary, f, indent=2)

	logging.info('Parallel run complete:')
	logging.info(json.dumps(summary, indent=2))
	logging.info(f'Summary saved to {out_file}')
	return 0


def update_globals(processes: int, batch_size: int, ticker_file: str, results_dir: str, only_missing: bool, use_scrapingbee: bool):
	"""Update global variables with CLI arguments"""
	global NUM_PROCESSES, BATCH_SIZE, TICKER_FILE, RESULTS_DIR, ONLY_MISSING, USE_SCRAPINGBEE
	NUM_PROCESSES = max(1, processes)
	BATCH_SIZE = max(1, batch_size)
	TICKER_FILE = ticker_file
	RESULTS_DIR = results_dir
	ONLY_MISSING = bool(only_missing)
	USE_SCRAPINGBEE = bool(use_scrapingbee)


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Parallel Yahoo Finance scraping')
	parser.add_argument('-n', '--limit', type=int, default=None,
		help='Number of tickers to process (omit or <=0 for all)')
	parser.add_argument('-p', '--processes', type=int, default=6,
		help='Number of parallel processes (default: 6)')
	parser.add_argument('-b', '--batch-size', type=int, default=10,
		help='API sub-batch size per process call (default: 10)')
	parser.add_argument('-t', '--ticker-file', type=str, default='all_tickers_api.txt',
		help='Path to ticker list file (default: all_tickers_api.txt)')
	parser.add_argument('--tickers', type=str, default=None,
		help='Comma-separated list of specific tickers to process (overrides ticker file)')
	parser.add_argument('-o', '--results-dir', type=str, default='parallel_results',
		help='Directory to write summary JSON (default: parallel_results)')
	parser.add_argument('--use-scrapingbee', action='store_true',
		help='Route yfinance HTTP requests through ScrapingBee proxy (requires SCRAPINGBEE_API_KEY)')
	parser.add_argument('-m', '--only-missing', action='store_true',
		help='Process only tickers that do not have data for today in the DB')

	args = parser.parse_args()

	# Apply CLI settings
	update_globals(args.processes, args.batch_size, args.ticker_file, args.results_dir, args.only_missing, args.use_scrapingbee)
	limit_val = None if (args.limit is None or args.limit <= 0) else args.limit

	raise SystemExit(main(limit=limit_val, ticker_list=args.tickers))
