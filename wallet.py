import asyncio
import bitcoinlib
from bitcoinlib.wallets import Wallet, wallet_create_or_open
from bitcoinlib.transactions import Transaction
from bitcoinlib.services.services import Service

from config import priv_key, wallet_name

async def open_wallet():
    wallet = await asyncio.to_thread(wallet_create_or_open, wallet_name, keys = priv_key)
    return wallet

async def get_addr(wallet):
    await asyncio.to_thread(wallet.scan)
    keys = await asyncio.to_thread(wallet.keys)

    # Выводим список адресов
    print("Список адресов кошелька:")
    for key in keys:
        print(f'сеть: {key.network.name}, ID: {key.id} адрес: {key.address}')

async def create_new_net(wallet, network):
    await asyncio.to_thread(wallet.scan)
    await asyncio.to_thread(wallet.new_key, network = network)

async def get_balance(wallet):
    await asyncio.to_thread(wallet.scan)

    print(f"Bitcoin баланс: {await asyncio.to_thread(wallet.balance, network='bitcoin')/100_000_000:.8f}")
    print(f"Testnet баланс: {await asyncio.to_thread(wallet.balance, network='testnet')/100_000_000:.8f}")
    print(f"Litecoin баланс: {await asyncio.to_thread(wallet.balance, network='litecoin')/100_000_000:.8f}")

async def get_fee(wallet, send_address, amount):
    await asyncio.to_thread(wallet.scan)

    # Получаем список доступных UTXO
    utxos = await asyncio.to_thread(wallet.utxos)
    
    # Если UTXO нет, возвращаем ошибку
    if not utxos:
        print(utxos)
        raise Exception("Нет доступных UTXO для создания транзакции.")
    
    # Создаем транзакцию (без отправки)
    transaction = await asyncio.to_thread(
        wallet.transaction_create,
        outputs=[(send_address, amount)],  # Адрес получателя и сумма
        fee=0,  # Пока не указываем комиссию
        broadcast=False  # Не отправляем транзакцию
    )
    
    # Рассчитываем размер транзакции
    transaction_size = await asyncio.to_thread(lambda: transaction.size())
    
    # Оцениваем комиссию с помощью estimate_fee
    fee_estimate = await asyncio.to_thread(Service.estimatefee, blocks = 1)
    
    # Рассчитываем комиссию
    fee_satoshis = fee_estimate  # Комиссия в сатоши
    fee_btc = fee_satoshis / 100_000_000  # Переводим в BTC
    
    return {
        "transaction_size_bytes": transaction_size,
        "fee_satoshis": fee_satoshis,
        "fee_btc": fee_btc,
    }

async def main():
    wallet = await open_wallet()
    send_addr = '1SdjgfhHDSFsdgtyuNSETYbvhEBjdsgUGRjdf'
    amount = 0.003
    #await send_btc(wallet, send_addr, amount)
    #await create_new_net(wallet, 'litecoin')
    #await get_balance(wallet)
    await get_addr(wallet)

if __name__=='__main__':
    asyncio.run(main())
