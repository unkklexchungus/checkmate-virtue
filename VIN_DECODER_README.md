# VIN Decoder CLI

A command-line interface for decoding Vehicle Identification Numbers (VINs) using the API Verve VIN Decoder service.

## Features

- 🚗 Decode VINs to get vehicle information
- 📱 Interactive mode for multiple VIN lookups
- 🔧 Command-line mode for single VIN decoding
- ✅ VIN format validation
- 🎨 Beautiful formatted output
- 🔑 API key configuration support

## Installation

The VIN decoder CLI is already set up in this project. Make sure you have Node.js installed and the dependencies are installed:

```bash
npm install
```

## Configuration

The API key is already configured in the script. If you need to use a different API key, you can:

1. Set an environment variable:
   ```bash
   export VIN_DECODER_API_KEY="your-api-key-here"
   ```

2. Or modify the `vin_decoder_cli.js` file directly.

## Usage

### Command Line Mode

Decode a single VIN by passing it as an argument:

```bash
# Using node directly
node vin_decoder_cli.js 1HGBH41JXMN109186

# Using npm script
npm run decode 1HGBH41JXMN109186

# Using the test script
npm test
```

### Interactive Mode

Run the script without arguments to enter interactive mode:

```bash
# Using node directly
node vin_decoder_cli.js

# Using npm script
npm start
```

In interactive mode, you can:
- Enter VINs one by one
- Type "quit" or "exit" to close the application
- Use Ctrl+C to exit at any time

### Example Output

```
🚗 VIN Decoder CLI
==================
API Key: ✅ Configured

🔍 Decoding VIN: 1HGBH41JXMN109186

✅ VIN Decoded Successfully!
==================================================
📅 Year: 1991
🏭 Make: HONDA
🚗 Model: N/A
🎨 Trim: N/A
🔧 Engine: N/A
⚙️ Transmission: N/A
🚪 Body Style: N/A
⛽ Fuel Type: N/A
🌍 Country: N/A
🏢 Manufacturer: AMERICAN HONDA MOTOR CO., INC.
==================================================
```

## VIN Format

The CLI validates VIN format before making API calls. A valid VIN must:
- Be exactly 17 characters long
- Contain only letters and numbers
- Exclude the letters I, O, and Q (which are not used in VINs)

## Integration with Python Service

The VIN decoder CLI can be used alongside the existing Python VIN decoder service. The Python service uses the NHTSA API as a fallback, while this CLI uses the API Verve service for more comprehensive data.

## Error Handling

The CLI handles various error scenarios:
- Invalid VIN format
- API errors
- Network connectivity issues
- Missing API key

## Available Commands

- `node vin_decoder_cli.js [VIN]` - Decode a specific VIN
- `node vin_decoder_cli.js` - Enter interactive mode
- `npm start` - Start interactive mode
- `npm run decode [VIN]` - Decode a specific VIN
- `npm test` - Test with a sample VIN

## API Information

This CLI uses the [API Verve VIN Decoder](https://apiverve.com/apps/vindecoder) service, which provides comprehensive vehicle information including:
- Year, Make, Model
- Engine specifications
- Transmission type
- Body style
- Fuel type
- Country of origin
- Manufacturer information
- Recall information (if available)
