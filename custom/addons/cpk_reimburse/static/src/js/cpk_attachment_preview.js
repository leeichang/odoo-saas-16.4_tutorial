/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";
import { useRef, onPatched } from "@odoo/owl";

export class CpkAttachmentPreviewField extends Many2ManyBinaryField {
    
    setup() {
        super.setup();
        this.rootRef = useRef("root");
        
        // 在組件渲染後添加預覽按鈕
        onPatched(() => {
            this.addPreviewButtons();
        });
    }

    get uploadText() {
        return "拖拽檔案到此處或點擊上傳憑證";
    }

    get acceptedFileExtensions() {
        return ".pdf,.jpg,.jpeg,.png,.gif,.bmp,.tiff";
    }

    getFileIconClass(record) {
        const fileName = record.data.display_name || record.data.name || "";
        const ext = fileName.split('.').pop()?.toLowerCase() || "";
        
        switch(ext) {
            case 'pdf': return 'fa fa-file-pdf-o text-danger';
            case 'jpg': case 'jpeg': case 'png': case 'gif': case 'bmp': 
                return 'fa fa-file-image-o text-info';
            case 'doc': case 'docx': 
                return 'fa fa-file-word-o text-primary';
            case 'xls': case 'xlsx': 
                return 'fa fa-file-excel-o text-success';
            default: 
                return 'fa fa-file-o';
        }
    }

    addPreviewButtons() {
        // 在標準Many2ManyBinaryField模板渲染後添加預覽按鈕
        if (!this.rootRef.el) return;
        
        // 找到所有attachment項目
        const attachments = this.rootRef.el.querySelectorAll('.o_attachment');
        
        attachments.forEach((attachment, index) => {
            // 檢查是否已經有預覽按鈕
            if (attachment.querySelector('.o_preview_btn')) return;
            
            const record = this.props.value?.data?.[index];
            if (!record) return;
            
            // 找到文件名連結
            const nameLink = attachment.querySelector('.o_attachment_name');
            if (!nameLink) return;
            
            // 創建預覽按鈕
            const previewBtn = document.createElement('button');
            previewBtn.type = 'button';
            previewBtn.className = 'btn btn-sm btn-outline-primary ms-1 o_preview_btn';
            previewBtn.title = '預覽憑證';
            previewBtn.innerHTML = '<i class="fa fa-eye"/>';
            
            // 添加點擊事件
            previewBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.onFilePreview(record);
            });
            
            // 插入預覽按鈕到文件名後面
            nameLink.parentNode.insertBefore(previewBtn, nameLink.nextSibling);
        });
        
        // 更新上傳區域的文字
        const uploadArea = this.rootRef.el.querySelector('.o_form_binary_form');
        if (uploadArea) {
            const label = uploadArea.querySelector('label, .o_select_file_button');
            if (label && !label.dataset.customized) {
                label.innerHTML = '<i class="fa fa-upload"/> 拖拽檔案到此處或點擊上傳憑證';
                label.dataset.customized = 'true';
            }
        }
    }

    async onFileUploaded(info) {
        // 呼叫父類的上傳方法
        await super.onFileUploaded(info);
        
        // 上傳完成後的自定義處理
        if (this.env.services.notification) {
            this.env.services.notification.add("憑證檔案上傳成功！", {
                type: "success",
            });
        }
    }

    getFileUrl(record) {
        // 返回檔案預覽URL
        return `/web/content/${record.resId}?download=false`;
    }

    onFilePreview(record) {
        // 處理檔案預覽
        const url = this.getFileUrl(record);
        
        // 檢查檔案類型
        const fileName = record.data.display_name || record.data.name || "";
        const ext = fileName.split('.').pop()?.toLowerCase() || "";
        
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
            // 圖片檔案 - 在新視窗開啟
            window.open(url, '_blank');
        } else if (ext === 'pdf') {
            // PDF檔案 - 在新視窗開啟
            window.open(url, '_blank');
        } else {
            // 其他檔案 - 直接下載
            const downloadUrl = `/web/content/${record.resId}?download=true`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    async onFileRemove(record) {
        // 移除檔案前的確認
        if (this.env.services.dialog) {
            try {
                const confirmed = await this.env.services.dialog.add(
                    "確認刪除",
                    "確定要刪除此憑證檔案嗎？",
                    {
                        confirmText: "刪除",
                        cancelText: "取消",
                    }
                );
                if (confirmed) {
                    return super.onFileRemove(record);
                }
            } catch (error) {
                // 如果dialog出錯，直接刪除
                return super.onFileRemove(record);
            }
        } else {
            // 如果沒有dialog服務，直接刪除
            return super.onFileRemove(record);
        }
    }
}

CpkAttachmentPreviewField.template = "cpk_reimburse.CpkAttachmentPreviewField";
CpkAttachmentPreviewField.supportedTypes = ["many2many"];

registry.category("fields").add("cpk_attachment_preview", CpkAttachmentPreviewField);