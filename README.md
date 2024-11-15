# ENBW Home Assistant Integration

This custom Home Assistant integration fetches data from public charging stations using [ENBW](https://www.enbw.com/elektromobilitaet/produkte/mobilityplus-app/ladestation-finden/map).

Feel free to provide feedback or contribute to this integration.

## Configuration

To add a charging point, you need the following information:

- **Id**: The id of the charging station. This can be found using the map (see link above). Check the network request when you click on a charging point.
- **API key (optional)**: In case the API key has been changed, the new key can be provided.

## License

MIT. See the [LICENSE](LICENSE) file for more details.

## Credits

Based on the Cowboy integration [elsbrock/cowboy-ha](https://github.com/elsbrock/cowboy-ha) (MIT).

Parts of the repository were copied over from [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint/) (MIT).