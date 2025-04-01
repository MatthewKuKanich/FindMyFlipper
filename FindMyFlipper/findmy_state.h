#pragma once

#include <extra_beacon.h>

#define FINDMY_STATE_HEADER "FindMy Flipper State"
#define FINDMY_STATE_VER 1
#define FINDMY_STATE_DIR EXT_PATH("apps_data/findmy")
#define FINDMY_STATE_PATH FINDMY_STATE_DIR "/findmy_state.txt"

#define BATTERY_FULL 0x00
#define BATTERY_MEDIUM 0x50
#define BATTERY_LOW 0xA0
#define BATTERY_CRITICAL 0xF0

typedef enum {
    FindMyTypeApple,
    FindMyTypeSamsung,
    FindMyTypeTile,
    FindMyTypeGoogle,
} FindMyType;

typedef struct {
    bool beacon_active;
    uint8_t broadcast_interval;
    uint8_t transmit_power;
    bool show_mac;
    uint8_t mac[EXTRA_BEACON_MAC_ADDR_SIZE];
    uint8_t data[EXTRA_BEACON_MAX_DATA_SIZE];
    FindMyType tag_type;

    // Generated from the other state values
    GapExtraBeaconConfig config;

    uint8_t battery_level;
} FindMyState;

bool findmy_state_load(FindMyState* out_state);

void findmy_state_apply(FindMyState* state);

void findmy_state_sync_config(FindMyState* state);

void findmy_state_save(FindMyState* state);

void findmy_update_payload_battery(uint8_t* data, uint8_t battery_level, FindMyType type);

uint8_t findmy_state_data_size(FindMyType type);
