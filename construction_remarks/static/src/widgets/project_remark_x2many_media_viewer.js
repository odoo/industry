import { registry } from "@web/core/registry";
import { x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { getVideoUrl } from "@html_editor/utils/url";
import { X2ManyMediaViewer } from "@html_editor/fields/x2many_field/x2many_media_viewer"

export class ProjectRemarkX2ManyMediaViewer extends X2ManyMediaViewer {
    setup() {
        super.setup();
        this.supportedFields.push("x_image_1920");
    }

    onVideoSave(videoInfo) {
        const url = getVideoUrl(videoInfo[0].platform, videoInfo[0].videoId, videoInfo[0].params);
        const videoList = this.props.record.data[this.props.name];
        videoList.addNewRecord({ position: "bottom" }).then((record) => {
            record.update({ x_name: videoInfo[0].platform + " - [Video]", x_video_url: url.href });
        });
    }

    async onImageSave(attachments) {
        let saved = await this.props.record.save();  // have to have a remark ID and a remark name
        if (!saved) return;  // if any field missing, abort 
        const attachmentIds = attachments.map((attachment) => attachment.id);
        const attachmentRecords = await this.orm.searchRead(
            "ir.attachment",
            [["id", "in", attachmentIds]],
            ["id", "datas", "name", "mimetype"],
            {}
        );
        for (const attachment of attachmentRecords) {
            const imageList = this.props.record.data[this.props.name];
            if (!attachment.datas) {
                // URL type attachments are mostly demo records which don't have any ir.attachment datas
                // TODO: make it work with URL type attachments
                return this.notification.add(
                    `Cannot add URL type attachment "${attachment.name}". Please try to reupload this image.`,
                    {
                        type: "warning",
                    }
                );
            }
            if (
                this.props.convertToWebp &&
                !["image/gif", "image/svg+xml"].includes(attachment.mimetype)
            ) {
                // This method is widely adapted from onFileUploaded in ImageField.
                // Upon change, make sure to verify whether the same change needs
                // to be applied on both sides.
                // Generate alternate sizes and format for reports.
                const image = document.createElement("img");
                image.src = `data:${attachment.mimetype};base64,${attachment.datas}`;
                await new Promise((resolve) => image.addEventListener("load", resolve));

                const originalSize = Math.max(image.width, image.height);
                const smallerSizes = [1024, 512, 256, 128].filter((size) => size < originalSize);
                let referenceId = undefined;

                for (const size of [originalSize, ...smallerSizes]) {
                    const ratio = size / originalSize;
                    const canvas = document.createElement("canvas");
                    canvas.width = image.width * ratio;
                    canvas.height = image.height * ratio;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(
                        image,
                        0,
                        0,
                        image.width,
                        image.height,
                        0,
                        0,
                        canvas.width,
                        canvas.height
                    );

                    // WebP format
                    const webpData = canvas.toDataURL("image/webp").split(",")[1];
                    const [resizedId] = await this.orm.call("ir.attachment", "create_unique", [
                        [
                            {
                                name: attachment.name.replace(/\.[^/.]+$/, ".webp"),
                                description: size === originalSize ? "" : `resize: ${size}`,
                                datas: webpData,
                                res_id: referenceId,
                                res_model: "ir.attachment",
                                mimetype: "image/webp",
                            },
                        ],
                    ]);

                    referenceId = referenceId || resizedId;

                    // JPEG format for compatibility
                    const jpegData = canvas.toDataURL("image/jpeg").split(",")[1];
                    await this.orm.call("ir.attachment", "create_unique", [
                        [
                            {
                                name: attachment.name.replace(/\.[^/.]+$/, ".jpg"),
                                description: `resize: ${size} - format: jpeg`,
                                datas: jpegData,
                                res_id: resizedId,
                                res_model: "ir.attachment",
                                mimetype: "image/jpeg",
                            },
                        ],
                    ]);
                }
                const canvas = document.createElement("canvas");
                canvas.width = image.width;
                canvas.height = image.height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(image, 0, 0, image.width, image.height);

                const webpData = canvas.toDataURL("image/webp").split(",")[1];
                attachment.datas = webpData;
                attachment.mimetype = "image/webp";
                attachment.name = attachment.name.replace(/\.[^/.]+$/, ".webp");
            }

            imageList.addNewRecord({ position: "bottom" }).then(async (record) => {
                const activeFields = imageList.activeFields;
                const updateData = {
                    x_name: attachment.name || this.props.context.default_name,
                    x_remark_id: this.props.context.default_x_remark_id,

                };
                for (const field in activeFields) {
                    if (attachment.datas && this.supportedFields.includes(field)) {
                        updateData[field] = attachment.datas;
                    }
                }
                record.update(updateData);
            });
        }
    }
}

export const projectRemarkX2ManyMediaViewer = {
    ...x2ManyField,
    component: ProjectRemarkX2ManyMediaViewer,
    extractProps: (
        { attrs, relatedFields, viewMode, views, widget, options, string },
        dynamicInfo
    ) => {
        const x2ManyFieldProps = x2ManyField.extractProps(
            { attrs, relatedFields, viewMode, views, widget, options, string },
            dynamicInfo
        );
        console.log("props", x2ManyFieldProps)
        return {
            ...x2ManyFieldProps,
            convertToWebp: options.convert_to_webp,
        };
    },
};

registry.category("fields").add("project_remark_x2_many_media_viewer", projectRemarkX2ManyMediaViewer);
