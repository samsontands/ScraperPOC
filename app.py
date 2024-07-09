import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_product_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', class_='product')
        
        links = []
        for product in products:
            link = product.find('a')['href']
            if not link.startswith('http'):
                link = 'https://www.i-machine.net' + link
            links.append(link)
        
        return links
    except Exception as e:
        st.error(f"An error occurred while fetching links: {str(e)}")
        return []

def scrape_product_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {'URL': url}
        
        # Extract model
        model_elem = soup.find('h1', style='margin: auto;')
        data['Model'] = model_elem.text.strip() if model_elem else 'N/A'
        
        # Extract price (updated to match the specified structure)
        price_elem = soup.find('div', class_='col-xs-12 color_orange fs36 bolder detailresfs3')
        data['Price'] = price_elem.text.strip() if price_elem else 'N/A'
        
        # Extract other details
        details = soup.find_all('div', class_='col-xs-12 paddTB10 product_detail_divider paddL20')
        for detail in details:
            detail_text = detail.text.strip()
            if ':' in detail_text:
                key, value = detail_text.split(':', 1)
                data[key.strip()] = value.strip()
            else:
                data[f'Additional Info {len(data)}'] = detail_text

        # Extract specification
        spec_elem = soup.find('span', style='font-weight: bolder;color: red;')
        if spec_elem:
            data['Specification'] = spec_elem.text.strip()
        
        return data
    except Exception as e:
        st.error(f"An error occurred while scraping {url}: {str(e)}")
        return None

def main():
    st.title('i-Machine Bulk Product Scraper POC')

    base_url = 'https://www.i-machine.net/'
    
    if st.button('Scrape Products'):
        with st.spinner('Fetching product links...'):
            product_links = get_product_links(base_url)
        
        if product_links:
            st.success(f"Found {len(product_links)} product links. Starting to scrape...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            scraped_data = []
            for index, link in enumerate(product_links):
                status_text.text(f"Scraping product {index+1} of {len(product_links)}")
                product_data = scrape_product_details(link)
                if product_data:
                    scraped_data.append(product_data)
                progress_bar.progress((index + 1) / len(product_links))
                time.sleep(1)  # Adding a delay to avoid overwhelming the server
            
            if scraped_data:
                df = pd.DataFrame(scraped_data)
                st.write(df)
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='i_machine_product_data.csv',
                    mime='text/csv',
                )
            else:
                st.warning("No data was scraped. Please check the console for error messages.")
        else:
            st.warning("No product links were found.")

    # Add a section to display the code at the bottom
    st.subheader("Source Code")
    with open(__file__, 'r') as file:
        code = file.read()
    st.code(code, language='python')

if __name__ == "__main__":
    main()
