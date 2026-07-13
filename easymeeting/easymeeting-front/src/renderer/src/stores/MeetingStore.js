import { defineStore } from "pinia";
export const useMeetingStore = defineStore('meetingInfo', {
    state: () => {
        return {
            memberList: [],
            allMemberList: [],
            lastUpdate: null,
            noReadChatCount: 0,
            chatOpen: false,
            inMeeting: false,
        }
    },
    actions: {
        setMemberList(memberList) {
            this.memberList = memberList;
        },
        setAllMemberList(allMemberList) {
            this.allMemberList = allMemberList;
        },
        updateMeeting(inMeeting) {
            this.lastUpdate = new Date().getTime();
            this.inMeeting = inMeeting;
        },
        addNoReadChatCount() {
            if (this.chatOpen) {
                return;
            }
            this.noReadChatCount++;
        },
        updateChatOpen(open) {
            if (open) {
                this.noReadChatCount = 0;
            }
            this.chatOpen = open;
        },
    }
})