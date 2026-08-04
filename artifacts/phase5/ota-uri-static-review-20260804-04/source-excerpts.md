# DeviceSoftwareOTA URI static excerpts

These are JADX-derived line excerpts, not original source. Re-run the script against the hashed APK for regeneration.

## `local_uri_database_column` / `LocalURI` — `com/amazon/android/app/AmazonDownloadManagerHelper.java:164`

- Interpretation: The local downloaded file is represented separately from the remote URI.
- Decompiled line: `pendingUpdate.setLocalUri(Uri.parse("file://" + downloadStatus.getDestinationFilePath()));`

## `local_uri_database_column` / `setLocalUri` — `com/amazon/android/app/AmazonDownloadManagerHelper.java:164`

- Interpretation: The local downloaded file is represented separately from the remote URI.
- Decompiled line: `pendingUpdate.setLocalUri(Uri.parse("file://" + downloadStatus.getDestinationFilePath()));`

## `server_url_to_remote_uri` / `getUrl()` — `com/amazon/device/software/ota/db/PublishedUpdate.java:64`

- Interpretation: The server-provided update URL becomes the PublishedUpdate remote URI.
- Decompiled line: `this.mRemoteUri = URI.create(availableUpdatesContainer.getUrl());`

## `server_url_to_remote_uri` / `mRemoteUri` — `com/amazon/device/software/ota/db/PublishedUpdate.java:28`

- Interpretation: The server-provided update URL becomes the PublishedUpdate remote URI.
- Decompiled line: `private final URI mRemoteUri;`

## `server_url_to_remote_uri` / `URI.create` — `com/amazon/device/software/ota/db/PublishedUpdate.java:64`

- Interpretation: The server-provided update URL becomes the PublishedUpdate remote URI.
- Decompiled line: `this.mRemoteUri = URI.create(availableUpdatesContainer.getUrl());`

## `remote_uri_database_column` / `RemoteURI` — `com/amazon/device/software/ota/db/PublishedUpdate.java:80`

- Interpretation: PublishedUpdates persists the remote URI in the OTA database schema.
- Decompiled line: `this.mRemoteUri = URI.create(contentValues.getAsString("RemoteURI"));`

## `remote_uri_database_column` / `contentValues.put` — `com/amazon/device/software/ota/db/PublishedUpdate.java:203`

- Interpretation: PublishedUpdates persists the remote URI in the OTA database schema.
- Decompiled line: `contentValues.put("RemoteURI", this.mRemoteUri.toString());`

## `download_mapping` / `getOtaDownloadUrl` — `com/amazon/device/software/ota/tasks/download/DownloadStarter.java:41`

- Interpretation: DownloadStarter maps the URI and enqueues it through AmazonDownloadManager.
- Decompiled line: `String otaDownloadUrl = this.mDNWStateObservable.getOtaDownloadUrl(string);`

## `download_mapping` / `IAmazonDownloadManager` — `com/amazon/device/software/ota/tasks/download/DownloadStarter.java:21`

- Interpretation: DownloadStarter maps the URI and enqueues it through AmazonDownloadManager.
- Decompiled line: `final IAmazonDownloadManager mIAmazonDownloadManager;`

## `download_mapping` / `enqueue` — `com/amazon/device/software/ota/tasks/download/DownloadStarter.java:67`

- Interpretation: DownloadStarter maps the URI and enqueues it through AmazonDownloadManager.
- Decompiled line: `pendingUpdate.setDownloadId(this.mIAmazonDownloadManager.enqueue(createRequest(pendingUpdate)));`

## `query_input` / `AuthenticatedDeviceGetUpdatesQueryInput` — `com/amazon/device/software/ota/updatechecker/RequestBuilder.java:5`

- Interpretation: The request carries build dimensions and installed-package inventory.
- Decompiled line: `import com.amazon.devicesoftwaretracking.AuthenticatedDeviceGetUpdatesQueryInput;`

## `query_input` / `setBuildDimensions` — `com/amazon/device/software/ota/updatechecker/RequestBuilder.java:52`

- Interpretation: The request carries build dimensions and installed-package inventory.
- Decompiled line: `authenticatedDeviceGetUpdatesQueryInput.setBuildDimensions(this.mBuildDimensionsGenerator.generateBuildDimensions());`

## `query_input` / `setInventory` — `com/amazon/device/software/ota/updatechecker/RequestBuilder.java:53`

- Interpretation: The request carries build dimensions and installed-package inventory.
- Decompiled line: `authenticatedDeviceGetUpdatesQueryInput.setInventory(this.mInventoryGenerator.generateInventory());`

## `update_endpoint_default` / `getUpdatesUrlPathAndMethod` — `com/amazon/device/software/ota/util/settings/OTASettings.java:141`

- Interpretation: The APK contains a default authenticated update-query endpoint.
- Decompiled line: `return this.mSettingsManager.getString("getUpdatesUrlPathAndMethod", "https://softwareupdates.amazon.com/software/inventory2");`

## `update_endpoint_default` / `softwareupdates.amazon.com/software/inventory2` — `com/amazon/device/software/ota/util/settings/OTASettings.java:141`

- Interpretation: The APK contains a default authenticated update-query endpoint.
- Decompiled line: `return this.mSettingsManager.getString("getUpdatesUrlPathAndMethod", "https://softwareupdates.amazon.com/software/inventory2");`

## `remote_config_app` / `createForAppId` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:73`

- Interpretation: SettingsManager creates an Arcus remote-configuration client.
- Decompiled line: `this.mManager = remoteConfigurationManagerWrapper.createForAppId(context, "arn:aws:remote-config:us-west-2:426273902372:appConfig:a17uvcne");`

## `remote_config_app` / `426273902372` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:73`

- Interpretation: SettingsManager creates an Arcus remote-configuration client.
- Decompiled line: `this.mManager = remoteConfigurationManagerWrapper.createForAppId(context, "arn:aws:remote-config:us-west-2:426273902372:appConfig:a17uvcne");`

## `remote_config_app` / `appConfig:a17uvcne` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:73`

- Interpretation: SettingsManager creates an Arcus remote-configuration client.
- Decompiled line: `this.mManager = remoteConfigurationManagerWrapper.createForAppId(context, "arn:aws:remote-config:us-west-2:426273902372:appConfig:a17uvcne");`

## `remote_config_attributes` / `Build.SERIAL` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:74`

- Interpretation: The remote configuration request is keyed by device/build attributes.
- Decompiled line: `this.mManager.openAttributes().addAttribute("dsn", Build.SERIAL);`

## `remote_config_attributes` / `build_version` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:76`

- Interpretation: The remote configuration request is keyed by device/build attributes.
- Decompiled line: `this.mManager.openAttributes().addAttribute("build_version", Long.valueOf(deviceInfo.getBuildNumber()));`

## `remote_config_attributes` / `ota_group` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:84`

- Interpretation: The remote configuration request is keyed by device/build attributes.
- Decompiled line: `this.mManager.openAttributes().addAttribute("ota_group", lastCheckGroup);`

## `remote_config_sync` / `maybeSyncArcusConfig` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:78`

- Interpretation: OTA settings can be refreshed through the remote configuration client.
- Decompiled line: `maybeSyncArcusConfig();`

## `remote_config_sync` / `mManager.sync` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:151`

- Interpretation: OTA settings can be refreshed through the remote configuration client.
- Decompiled line: `this.mManager.sync(this.mArcusCallback);`
## `remote_config_sync` / `Twelve` — `com/amazon/device/software/ota/util/settings/SettingsManager.java:28`

- Interpretation: OTA settings can be refreshed through the remote configuration client.
- Decompiled line: `private static final long TWELVE_HOURS = TimeUnit.HOURS.toMillis(12);`

## `authenticated_update_post` / `AuthenticatedURLConnectionWrapper` — `com/amazon/device/software/tracking/service/GetUpdatesCall.java:12`

- Interpretation: The update query uses the authenticated URL wrapper and JSON POST.
- Decompiled line: `import com.amazon.identity.auth.device.api.AuthenticatedURLConnectionWrapper;`

## `authenticated_update_post` / `setRequestMethod("POST")` — `com/amazon/device/software/tracking/service/GetUpdatesCall.java:209`

- Interpretation: The update query uses the authenticated URL wrapper and JSON POST.
- Decompiled line: `httpURLConnectionOpenConnection.setRequestMethod("POST");`

## `authenticated_update_post` / `Content-Type` — `com/amazon/device/software/tracking/service/GetUpdatesCall.java:208`

- Interpretation: The update query uses the authenticated URL wrapper and JSON POST.
- Decompiled line: `httpURLConnectionOpenConnection.setRequestProperty("Content-Type", "application/json");`
