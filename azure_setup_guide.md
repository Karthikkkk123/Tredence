# Setting Up Azure API Keys

## Text Analytics API
1.  Go to the [Azure Portal](https://portal.azure.com/)
2.  Click "Create a resource"
3.  Search for "Text Analytics" and select it
4.  Click "Create"
5.  Fill in the required information:

    *   Subscription: Your Azure subscription
    *   Resource group: Create new or use existing
    *   Region: Choose a region close to you
    *   Name: Give your resource a unique name
    *   Pricing tier: Choose "Free" tier (F0) for testing
6.  Click "Review + create" and then "Create"
7.  Once deployment is complete, go to your resource
8.  Navigate to "Keys and Endpoint" in the left menu
9.  Copy "KEY 1" and the "ENDPOINT" URL
10. Update your `.env` file with these values:

    ```text
    TEXT_ANALYTICS_KEY=your_copied_key
    TEXT_ANALYTICS_ENDPOINT=your_copied_endpoint
    ```

## Personalizer API

1.  Go to the [Azure Portal](https://portal.azure.com/)
2.  Click "Create a resource"
3.  Search for "Personalizer" and select it
4.  Click "Create"
5.  Fill in the required information:

    *   Subscription: Your Azure subscription
    *   Resource group: Create new or use existing
    *   Region: Choose a region that supports Personalizer (e.g., West US 2)
    *   Name: Give your resource a unique name
    *   Pricing tier: Standard (S0)
6.  Click "Review + create" and then "Create"
7.  Once deployment is complete, go to your resource
8.  Navigate to "Keys and Endpoint" in the left menu
9.  Copy "KEY 1" and the "ENDPOINT" URL
10. Update your `.env` file with these values:

    ```text
    PERSONALIZER_KEY=your_copied_key
    PERSONALIZER_ENDPOINT=your_copied_endpoint
    ```

## Azure Communication Services

1.  Go to the [Azure Portal](https://portal.azure.com/)
2.  Click "Create a resource"
3.  Search for "Communication Services" and select it
4.  Click "Create"
5.  Fill in the required information:

    *   Subscription: Your Azure subscription
    *   Resource group: Create new or use existing
    *   Resource name: Give your resource a unique name
6.  Click "Review + create" and then "Create"
7.  Once deployment is complete, go to your resource
8.  Navigate to "Keys" in the left menu
9.  Copy the "CONNECTION STRING" or "PRIMARY KEY" and "ENDPOINT" URL
10. Update your `.env` file with these values:

    ```text
    COMMUNICATION_KEY=your_copied_key
    COMMUNICATION_ENDPOINT=your_copied_endpoint
    ```

## Face API

1.  Go to the [Azure Portal](https://portal.azure.com/)
2.  Click "Create a resource"
3.  Search for "Face" and select it
4.  Click "Create"
5.  Fill in the required information:

    *   Subscription: Your Azure subscription
    *   Resource group: Create new or use existing
    *   Region: Choose a region close to you
    *   Name: Give your resource a unique name
    *   Pricing tier: Choose "Free" tier (F0) for testing
6.  Click "Review + create" and then "Create"
7.  Once deployment is complete, go to your resource
8.  Navigate to "Keys and Endpoint" in the left menu
9.  Copy "KEY 1" and the "ENDPOINT" URL
10. Update your `.env` file with these values:

    ```text
    FACE_API_KEY=your_copied_key
    FACE_API_ENDPOINT=your_copied_endpoint
    ```

## Important Notes

*   Free tiers have limitations on the number of API calls you can make
*   Keep your API keys secure and never commit them to public repositories
*   For production applications, consider using Azure Key Vault to store keys
